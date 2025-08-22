##############################################################################
#
# Copyright (c) 2014 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Webtest browser
"""
__docformat__ = "reStructuredText"

import sys
import re
import time
import json
import io
import os
import itertools
import webbrowser
import tempfile
import collections
import wsgiproxy.proxies
from contextlib import contextmanager

import lxml.etree
import lxml.html

from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.element import NavigableString

from zope.interface import implementer
from zope.cachedescriptors.property import Lazy

from p01.testbrowser import interfaces
from p01.testbrowser._compat import httpclient
from p01.testbrowser._compat import PYTHON2
from p01.testbrowser._compat import urllib_request
from p01.testbrowser._compat import urlparse
import p01.testbrowser.cookies
import p01.testbrowser.html2text
import p01.testbrowser.xpath

import webtest.forms
import webtest.utils

import p01.testbrowser.app
import p01.testbrowser.control
import p01.testbrowser.exceptions
from p01.testbrowser.control import disambiguate
from p01.testbrowser.control import controlFormTupleRepr
from p01.testbrowser.control import zeroOrOne
from p01.testbrowser.control import isMatching
from p01.testbrowser.utils import SetattrErrorsMixin
from p01.testbrowser.xpath import getXPathSelector


PY2 = sys.version_info[0] == 2
if PY2:
    import __builtin__ as builtins
    text_type = unicode
    native_str_type = builtins.str
    binary_types = (str, bytearray)
    bytes_type = str
else:
    import builtins
    text_type = str
    native_str_type = str
    text_type = str
    binary_types = (bytes, bytearray)
    bytes_type = bytes
    basestring = str
    unicode = str


def _latin1(s):
    if PY2:
        if isinstance(s, text_type):
            return s.encode('latin-1')
        if isinstance(s, binary_types):
            return s
        return builtins.str(s)
    else:
        if isinstance(s, binary_types):
            return s.decode('latin-1')
        if isinstance(s, str):
            return s
        return str(s)

def _wsgi_status(status):
    if PY2:
        if type(status) is native_str_type:
            return status
        if isinstance(status, text_type):
            return status.encode('latin-1', 'strict')
        try:
            ba = bytearray(status)
            return ''.join(chr(c) for c in ba)
        except Exception:
            return native_str_type(status)
    else:
        return status if isinstance(status, str) else str(status)

def _wsgi_header_name(s):
    if PY2:
        if type(s) is native_str_type:
            return s
        if isinstance(s, text_type):
            return s.encode('latin-1', 'strict')
        try:
            return ''.join(chr(c) for c in bytearray(s))
        except Exception:
            return builtins.str(s)
    else:
        if isinstance(s, binary_types):
            return s.decode('latin-1', 'strict')
        return s if isinstance(s, str) else str(s)

def _wsgi_header_value(s):
    # gleiche Logik wie Name
    return _wsgi_header_name(s) if PY2 else (
        s.decode('latin-1', 'strict') if isinstance(s, binary_types)
        else (s if isinstance(s, str) else str(s))
    )



DOM_WARNING_MESSAGE = """
=========================================================
Tag not found for update the dom.
Please provide a bit more attributes in your dom element.
At least an unique name or id is required in your forms
=========================================================
"""


###############################################################################
#
# BeautifulSoup (fix some rednering issues)

class TextAreaTag(Tag):
    """TextArea Tag"""

    def _should_pretty_print(self, indent_level):
        return False


class PreTag(Tag):
    """Pre Tag"""

    def _should_pretty_print(self, indent_level):
        return False


class NoTextAreaPrettifyBeautifulSoup(BeautifulSoup):
    """BeautifulSoup which doesn't prettify textarea tags

    Note: BeautifulSoup uses the a hardcoded class attribute reference for
    lookup the _should_pretty_print condition for each tag. This makes it
    impossible for apply a custom setup except we whould monkey patch
    the HTMLAwareEntitySubstitution class. But this could break other
    applications runtime processing. So let's use some custom Tag classes
    and hard code the conditions.

    Check the method _should_pretty_print in class Tag for this issue e.g.:
    self.name not in HTMLAwareEntitySubstitution.preformatted_tags

    Wihthout this bugfix, we whould get spaces in textarea values which could
    break the application testing.

    """

    def handle_starttag(self, name, namespace, nsprefix, attrs, sourceline=None,
                        sourcepos=None):
        """USe own tag classes for preserve pretty print"""
        self.endData()

        if (self.parse_only and len(self.tagStack) <= 1
            and (self.parse_only.text
                 or not self.parse_only.search_tag(name, attrs))):
            return None

        if name == 'textarea':
            tag = TextAreaTag(self, self.builder, name, namespace, nsprefix,
                attrs, self.currentTag, self._most_recent_element,
                sourceline=sourceline, sourcepos=sourcepos)
        elif name == 'pre':
            tag = PreTag(self, self.builder, name, namespace, nsprefix,
                attrs, self.currentTag, self._most_recent_element,
                sourceline=sourceline, sourcepos=sourcepos)
        else:
            tag = Tag(self, self.builder, name, namespace, nsprefix, attrs,
                self.currentTag, self._most_recent_element,
                sourceline=sourceline, sourcepos=sourcepos)
        if tag is None:
            return tag
        if self._most_recent_element is not None:
            self._most_recent_element.next_element = tag
        self._most_recent_element = tag
        self.pushTag(tag)
        return tag


def getBeautifulSoup(text, features='lxml'):
    """Return BeautifulSoup with html feature by default"""
    return NoTextAreaPrettifyBeautifulSoup(text, features)


def getTagsForContent(content):
    """Return clean tags without html/body wrapper"""
    return getBeautifulSoup(content, "html.parser")


###############################################################################
#
# container for controls outside form tag

class WebTestFormBugfix(webtest.forms.Form):
    """Fix parsing bug


    The webtest form dons't corretly parse the textarea content if the
    content starts with text and contains tags e.g.

    <testarea>some <b>important</b> stuff</textarea>

    This will loose the <b> tags.

    """

# XXX: review this! Should we also remove ending \n and \r\n?
#      This could help to solve the text area prettify issue we fixed
#      wit the NoTextAreaPrettifyBeautifulSoup implementation?
#      But I guess the NoTextAreaPrettifyBeautifulSoup bugfix is the better
#      and more correct bugfix
    def _parse_fields(self):
        fields = collections.OrderedDict()
        field_order = []
        tags = ('input', 'select', 'textarea', 'button')
        for pos, node in enumerate(self.html.findAll(tags)):
            attrs = dict(node.attrs)
            tag = node.name
            name = None
            if 'name' in attrs:
                name = attrs.pop('name')

            if tag == 'textarea':
                # if node.text.startswith('\r\n'):  # pragma: no cover
                #     text = node.text[2:]
                # elif node.text.startswith('\n'):
                #     text = node.text[1:]
                # else:
                #     text = node.text
                # attrs['value'] = text
                #
                # bugfix: extract content from node and don't use node.text
                # which will loose sub tags if the content starts with text
                # and includes sub tags in it's text string
                # simply use our xpath selector for extract the content. This
                # implementation knows how to get the real content for strings,
                # xml and mixed content
                nStr = '%s' % node
                selector = getXPathSelector(nStr)
                text = selector.extractContent('//textarea')

                # remove leading line breaks. This should be fixed without
                # NoTextAreaPrettifyBeautifulSoup bugfix. Should we include
                # leading line breaks? since the test browser doens't
                # implicit add them? Otherwiwse the test browser will remove
                # leading line breaks when the user explit will use them.
                if text.startswith('\r\n'):  # pragma: no cover
                    text = text[2:]
                elif text.startswith('\n'):
                    text = text[1:]
                attrs['value'] = text

            tag_type = attrs.get('type', 'text').lower()
            if tag == 'select':
                tag_type = 'select'
            if tag_type == "select" and "multiple" in attrs:
                tag_type = "multiple_select"
            if tag == 'button':
                tag_type = 'submit'

            FieldClass = self.FieldClass.classes.get(tag_type,
                                                     self.FieldClass)

            # https://github.com/Pylons/webtest/issues/73
            if sys.version_info[:2] <= (2, 6):
                attrs = dict((k.encode('utf-8') if isinstance(k, unicode)
                              else k, v) for k, v in attrs.items())

            # https://github.com/Pylons/webtest/issues/131
            reserved_attributes = ('form', 'tag', 'pos')
            for attr in reserved_attributes:
                if attr in attrs:
                    del attrs[attr]

            if tag == 'input':
                if tag_type == 'radio':
                    field = fields.get(name)
                    if not field:
                        field = FieldClass(self, tag, name, pos, **attrs)
                        fields.setdefault(name, []).append(field)
                        field_order.append((name, field))
                    else:
                        field = field[0]
                        assert isinstance(field,
                                          self.FieldClass.classes['radio'])
                    field.options.append((attrs.get('value'),
                                          'checked' in attrs,
                                          None))
                    field.optionPositions.append(pos)
                    continue
                elif tag_type == 'file':
                    if 'value' in attrs:
                        del attrs['value']

            field = FieldClass(self, tag, name, pos, **attrs)
            fields.setdefault(name, []).append(field)
            field_order.append((name, field))

            if tag == 'select':
                for option in node('option'):
                    field.options.append(
                        (option.attrs.get('value', option.text),
                         'selected' in option.attrs,
                         option.text))

        self.field_order = field_order
        self.fields = fields


class WebTestForm(WebTestFormBugfix):
    """Wrapper for webtest Form"""


class WebTestNonFormControls(WebTestFormBugfix):
    """Dummy control container for all controls outside a form

    We will remove all forms and contained controls. All controls not included
    in form tags will stay as is.

    This is required since we need to support j01.jsonrpc where a button
    outside a form can submit the form using javascript helpers. In general
    there is no need to submit forms only within submit buttons inside form
    if the button uses javascript. But note, this only works if the Browser
    instance knows how to handle the javascript button. j01.jsonrpc buttons
    will work out of the box but you can simply implement your own custom
    buttons and use getClickableControl in your Browser instance.

    """

    def __init__(self, response, text, parser_features='lxml'):
        self.response = response
        # remove all form tags
        html = getBeautifulSoup(text, parser_features)
        # remove fields inside form and apply prettify text
        for tag in html.select('form'):
            tag.extract()
        self.text = html.prettify()
        # setup soup again with removed form tags
        self.html = getBeautifulSoup(self.text, parser_features)
        self.action = None
        self.method = None
        self.id = None
        self.enctype = None
        self._parse_fields()

    def submit(self, name=None, index=None, value=None, **args):
        """Can't submit this form without a form tag"""
        raise p01.testbrowser.exceptions.BrowserStateError(
            "Can't submit a control without a form tag")

    def upload_fields(self):
        """Return a list of file field tuples"""
        return []

    def __repr__(self):
        return '<WebTestNonFormControls>'


###############################################################################
#
# timer

class PystoneTimer(object):
    start_time = 0
    end_time = 0
    # Default pystone value (typical benchmark result)
    _pystones_per_second = 50000.0

    @property
    def pystonesPerSecond(self):
        """Return fixed pystones value - no longer needs benchmarking"""
        return self._pystones_per_second

    def _getTime(self):
        # Use best available timer for the platform
        if sys.platform.startswith('win'):
            if hasattr(time, 'perf_counter'):  # Python 3+
                return time.perf_counter()
            return time.clock()  # Python 2 Windows fallback
        return time.time()  # Unix systems

    def start(self):
        """Begin a timing period"""
        self.start_time = self._getTime()
        self.end_time = None

    def stop(self):
        """End a timing period"""
        self.end_time = self._getTime()

    @property
    def elapsedSeconds(self):
        """Elapsed time in seconds"""
        end_time = self._getTime() if self.end_time is None else self.end_time
        return end_time - self.start_time

    @property
    def elapsedPystones(self):
        """Elapsed pystones (calculated using fixed ratio)"""
        return self.elapsedSeconds * self.pystonesPerSecond

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

###############################################################################
#
# avticity

class RelativeURLMixin(object):
    """Relative url mixin class"""

    browser = None

    def getRelativURL(self, url):
        # get relative url for given url
        if url and self.browser is not None:
            bURL = self.browser._getBaseUrl()
            parsed = urlparse.urlparse(bURL)
            baseURL = '%s://%s' % (parsed.scheme, parsed.netloc)
            if url == baseURL:
                url = '/'
            else:
                url = url.replace(baseURL, '')
        return url

    def simplify(self, content):
        # replace all kind of relative url in a string
        if content and self.browser is not None:
            bURL = self.browser._getBaseUrl()
            parsed = urlparse.urlparse(bURL)
            baseURL = '%s://%s' % (parsed.scheme, parsed.netloc)
            baseAndSpace = '%s ' % baseURL
            baseAndSpaceWithSlash = '%s/ ' % baseURL
            if content.endswith(baseURL):
                # one more special case if message ends with base url but
                # has no space at the end
                # e.g. <open http://127.0.0.1:8080>
                content = content[:-len(baseURL)]
                content += '/'
            content = content.replace(baseAndSpaceWithSlash, '/ ')
            content = content.replace(baseAndSpace, '/ ')
            content = content.replace(baseURL, '')
        return content


class Activity(RelativeURLMixin):
    """Generic activity supporting a mesage and kw args.

    You can simply use a representation string as message and optional
    include any keyword data which can get represented as string. We will
    render the given message inclding the optional data.

    """

    def __init__(self, msg, **data):
        self.msg = msg
        self.data = data

    def render(self, prettify=False):
        """Represent activity"""
        data = {}
        for k, v in self.data.items():
            try:
                # convert to string
                v = '%s' % v
            except Exception as e:
                # mark as failed
                v = 'NOSTRING'
            data[k] = v
        msg = self.msg % data
        return '<%s>' % self.simplify(msg)

    def __repr__(self):
        return self.render(prettify=False)


class DocumentReadyActivity(object):
    """Document ready activity"""

    def __init__(self, browser):
        self.dom = browser._dom

    def render(self, prettify=False):
        """Represent activity"""
        return '<DOCUMENT ready %s>' % len(self.dom)

    def __repr__(self):
        return self.render(prettify=False)


class RequestActivity(object):
    """RequestActivity entry"""

    def __init__(self, response, dom, title=None):
        self.response = response
        self.dom = dom
        self.title = title

    def render(self, prettify=False):
        """Represent activity"""
        # request
        if self.response.request.path:
            path = ' %s' % self.response.request.path
        else:
            path = ' /'
        if self.response.request.content_type:
            # POST request
            ct = ' %s' % self.response.request.content_type
        else:
            # GET request
            ct = ''
        # response
        if self.response.content_type:
            rct = ' %s' % self.response.content_type
        else:
            rct = ''
        if self.response.body:
            body = ' %s' % len(self.response.body)
        else:
            body = ' no body'
        # return request/response representation
        req = '%s%s%s' % (self.response.request.method, path, ct)
        resp =  '%s%s%s' %(self.response.status, rct, body)
        if prettify and len(req + resp) > 70:
            space = ' ' * (len(self.response.request.method) + 2)
            resp = '\n%s%s' % (space, resp)
        else:
            resp = ' %s' % resp
        if prettify:
            return '<%s%s>' % (req, resp)
        else:
            return '<%s%s>' % (req, resp)

    def __repr__(self):
        return self.render(prettify=False)


class HistoryPushStateActivity(RelativeURLMixin):
    """Browser history push state cactivity"""

    browser = None

    def __init__(self, data):
        # pushState url and title attributes
        self.url = data.get('url')
        self.title =  data.get('title')
        # j01.jsonrpc.js state data
        self.cbURL =  data.get('cbURL')
        self.method =  data.get('method')
        self.params =  data.get('params')
        self.onSuccess =  data.get('onSuccess')
        self.onError =  data.get('onError')
        self.onTimeout =  data.get('onTimeout')

    def render(self, prettify=False):
        """Represent activity"""
        if self.cbURL:
            if self.params:
                params = ' params:%s' % json.dumps(self.params)
            else:
                params = ''
            cbURL = self.getRelativURL(self.cbURL)
            url = ' %s %s %s' % (self.method, cbURL, params)
        elif self.url:
            url = ' %s' % self.getRelativURL(self.url)
        else:
            url = ' missing url'
        return '<PUSH STATE%s>' % url

    def __repr__(self):
        return self.render(prettify=False)


class HistoryPopStateActivity(RelativeURLMixin):
    """Browser history pop state cactivity"""

    browser = None

    def __init__(self, state=None):
        self.state = state

    def render(self, prettify=False):
        """Represent activity"""
        if self.state:
            if self.state.cbURL:
                if self.state.params:
                    params = ' params:%s' % json.dumps(self.state.params)
                else:
                    params = ''
                cbURL = self.getRelativURL(self.state.cbURL)
                url = ' %s %s%s' % (self.state.method, cbURL, params)
            elif self.state.url:
                url = ' url:%s' % self.getRelativURL(self.state.url)
            else:
                url = ' missing url'
        else:
            url = ''
        return '<POP STATE%s>' % url

    def __repr__(self):
        return self.render(prettify=False)


class Activities(object):
    """Request/response acvitities"""

    def __init__(self, browser):
        self.browser = browser
        # last in first out
        self._data = []

    def clear(self):
        del self._data[:]

    def doAddActivity(self, activity, **data):
        """Add given activity"""
        if isinstance(activity, (str, basestring, bytes)):
            # add generic activity based on given pattern
            activity = Activity(activity, **data)
        activity.browser = self.browser
        self._data.append(activity)

    def doDocumentReady(self):
        obj = DocumentReadyActivity(self.browser)
        self.doAddActivity(obj)

    # testing helper
    def getActivities(self, prettify=True):
        """Get the activity history"""
        if prettify:
            for entry in self._data:
                print(entry.render(prettify=True))
        else:
            return self._data

    def __repr__(self):
        return '<%s len=%s>' % (self.__class__.__name__, len(self._data))


class ActivitiesMixin(object):
    """Activites mixin class"""

    activities = None

    def __init__(self):
        # setup activities
        super(ActivitiesMixin, self).__init__()
        self.activities = Activities(self)

    def doAddActivity(self, activity, **data):
        self.activities.doAddActivity(activity, **data)

    def doDocumentReady(self):
        self.activities.doDocumentReady()

    def getActivities(self, prettify=True):
        return self.activities.getActivities(prettify)


###############################################################################
#
# history

class HistoryEntry(object):
    """History entry"""

    def __init__(self, response, dom, state=None, title=None, url=None):
        self.response = response
        self.dom = dom
        self.state = state
        self.title = title
        self.url = url

    def render(self, prettify=False):
        """Represent activity"""
        # request
        if self.response.request.path:
            path = ' %s' % self.response.request.path
        else:
            path = ' /'
        if self.response.request.content_type:
            # POST request
            ct = ' %s' % self.response.request.content_type
        else:
            # GET request
            ct = ''
        # response
        if self.response.content_type:
            rct = ' %s' % self.response.content_type
        else:
            rct = ''
        if self.response.body:
            body = ' %s' % len(self.response.body)
        else:
            body = ' no body'
        # return request/response representation
        req = '%s%s%s' % (self.response.request.method, path, ct)
        resp =  '%s%s%s' %(self.response.status, rct, body)
        if prettify and len(req + resp) > 70:
            space = ' ' * (len(self.response.request.method) + 2)
            resp = '\n%s%s' % (space, resp)
        else:
            resp = ' %s' % resp
        if prettify:
            return '<%s%s>' % (req, resp)
        else:
            return '<%s%s>' % (req, resp)

    def __repr__(self):
        return self.render(prettify=False)


class J01HistoryState(object):
    """History state implementation like given in j01.history.js"""

    def __init__(self, data):
        # pushState url and title attributes
        self.url = data.get('url')
        self.title =  data.get('title')
        # j01.jsonrpc.js state data
        self.cbURL =  data.get('cbURL')
        self.method =  data.get('method')
        self.params =  data.get('params')
        self.onSuccess =  data.get('onSuccess')
        self.onError =  data.get('onError')
        self.onTimeout =  data.get('onTimeout')
        self.timestamp = time.time()


class HTML5History(object):
    """HTML5 history simulation

    Note: this implementaiton provides the javascript history concept
    implemented as j01.history.js from the j01.jsonrpc package.
    This loosly implementes the HTML5 browser history api and offers
    processing jsonrpc requests on pop state events which are simulated
    with the history back and go and onpopstate methods.

    You can simple call browser.goBack or browser.goForward for navigate
    with the history api.

    The methods pushState and replaceState are only internal used and
    you probably don't need them for testing.

    The j01.history.js implementation will make sure, that if we load an
    initial page, that the loaded page get added to the history. This allows us
    to navigate allways back to the initial page. This implementation
    will only add a reponse to the history before processing the next request.
    This is because we can access the current response at any and add them
    to the history before make a new request. This is not possible in the
    javascript api.

    HEADSUP: In WebKit browsers, a popstate event would be triggered after
    document's onload event, but Firefox and IE do not have this behavior.
    The j01.history.js implementation will block such to early fired events.

    """

    def __init__(self, browser):
        super(HTML5History, self).__init__()
        self.browser = browser
        # last in first out
        self._data = []

    # helpers
    def _add(self, entry):
        self._data.append(entry)

    def clear(self):
        del self._data[:]

    # testing helper
    def getHistory(self, prettify=True):
        """Get the history"""
        if prettify:
            for entry in self._data:
                print(entry.render(prettify=True))
        else:
            return self._data

    # html5 api
    def pushState(self, response, dom, state=None, title=None, url=None):
        """Add history entry after each response"""
        if response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Already at start of history")
        # setup state
        entry = HistoryEntry(response, dom, state, title, url)
        self._add(entry)

    def replaceState(self, state, title, url):
        """Replace current (lastest) history entry"""
        # get current (latest) history entry
        try:
            old = self._data.pop()
        except IndexError:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Already at start of history")
        # set old response as current response
        self.browser.doResponse(old.response)
        # create and add new history entry
        entry = HistoryEntry(old.response, old.dom, state, title, url)
        self._add(old)

    # browser back/forward buttons
    def back(self, n):
        """Go back in history"""
        counter = n
        if n < 1:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "History back method requires a counter larger then: %s" % n)
        entry = None
        while n > 0:
            try:
                entry = self._data.pop()
            except IndexError:
                raise p01.testbrowser.exceptions.BrowserStateError(
                    "Already at start of history")
            n -= 1
        if entry is not None:
            # add activity
            msg = 'back %s' % counter
            self.browser.doAddActivity(msg)
            # start pop state
            self.browser.onPopState(entry)
            self.browser.doDocumentReady()
        else:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Internal browser history setup error, history entry is None")

    def go(self, n):
        """Go forward in history"""
        raise NotImplemented("Going forward in history is not supported yet")
        #self.browser.doDocumentReady()

    def __repr__(self):
        return '<%s len=%s>' % (self.__class__.__name__, len(self._data))


class HTML5HistoryMixin(object):
    """HTML5 history mixin class

    This history implementation simulates the j01.history.js concept. The
    most important thing to know about the j01.history.js concept is that we
    load the page content with j01LoadContent method. This means we can make
    sure that we don't show outdated content for any page.
    """

    # html5 like history
    history = None
    isPushState = None
    isOnPopState = None

    def __init__(self):
        super(HTML5HistoryMixin, self).__init__()
        # setup history
        self.history = HTML5History(self)

    # j01.jsonrpc.js history api
    def j01PushState(self, response, dom, title):
        """Push state handler simulating j01.history.js implementation

        This method knows what's to do if we add a jsonrpc response to the
        history. This method simulates the j01.jsonrpc.js concept given from
        j01.jsonrpc.
        """
        # condition
        if response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No response given for push state")
        if self.isPushState is False:
            # marked for skip, reset skip marker
            self.isPushState = None
            return
        if response.content_type.endswith(('+json', '/json')):
            # this simulates a real browser history javacsript pushState call
            data = self.getJSONRPCResult(response)
            if isinstance(data, dict) and data.get('state') is not None:
                # only a dict result can contain a state, some other jsonrpc
                # method return a simple content string etc. This means we
                # can't process a history state
                # override given title and url
                title = data.get('stateTitle')
                url = data.get('stateURL')
                # setup state based on given state data
                sData = data['state']
                state = J01HistoryState(sData)
                # push state to history
                self.history.pushState(response, dom, state, title, url)
                # add history activity
                obj = HistoryPushStateActivity(sData)
                self.doAddActivity(obj)
        else:
            # this is not a real browser history javascript pushState call
            # but we add all our request/respone to the history
            state = None
            url = response.location
            # push state to history
            self.history.pushState(response, dom, state, title, url)

    def j01PopState(self, state=None):
        """Pop state handler simulating j01.history.js implementation

        This method knows how to process a history state pop'ed from the
        history by calling history.back(count) or browser.goBack(count).
        """
        if state is None:
            # no state given
            return
        # add marker for prevent adding a poping state to get added to the
        # history as a new entry because a poping state is only a
        # re-construction of a page dom and not a new loaded page
        self.isPushState = False
        if state.cbURL:
            # process jsonrpc using the method defined in state
            params = state.params
            if params is None:
                params = self.j01URLToArray(state.cbURL)
            onSuccess = self.j01GetCallback(state.onSuccess)
            onError = self.j01GetCallback(state.onError)
            self.doJSONRPCCall(state.cbURL, state.method, params, onSuccess,
                onError)
        elif state.url:
            # process simple get request. The response state cbURL must
            # explicit set to None for force such a use case.
            self.doRequest('GET', state.url)

    def onPopState(self, entry):
        """Process on pop state handling"""
        # reset response and dom with data given from history entry before
        # processing state. This sounds a bit curios but it is required if we
        # go back more then one page in history which is not possible with
        # the real browser history api. Just make sure we have the right
        # condition for apply the state. In other words this is not relevant
        # and will apply the same data as we already have if you just go one
        # page back.

        # add pop state activity
        obj = HistoryPopStateActivity(entry.state)
        self.doAddActivity(obj)
        # add isOnPopState marker before procesing
        self.isOnPopState = True
        self.doResponse(entry.response)
        dom = entry.dom
        self.setUpDom(dom)
        # process state
        if entry.state is not None:
            self.j01PopState(entry.state)
        else:
            msg = 'response replaced'
            self.doAddActivity(msg)
        # rest isOnPopState marker
        self.isOnPopState = None

    # testing helper
    def getHistory(self, prettify=True):
        """Returns the history entry items usable for introspection"""
        return self.history.getHistory(prettify)


###############################################################################
#
# j01.jsonrpc methods and callback handler

class JSONRPCCallbackMixin(object):
    """JSONRPC callback methods mixin class"""

    def __init__(self):
        super(JSONRPCCallbackMixin, self).__init__()
        self.j01CallbackRegistry = {}
        # j01.jsonrpc.js allbacks
        self.j01RegisterCallback('j01RenderContent', self.j01RenderContent)
        self.j01RegisterCallback('j01RenderContentSuccess',
            self.j01RenderContentSuccess)
        self.j01RegisterCallback('j01RenderContentError',
            self.j01RenderContentError)
        # j01.jsonrpc.js allbacks
        self.j01RegisterCallback('j01DialogRenderContent',
            self.j01DialogRenderContent)
        self.skipDomInjectionError = False

    # callback registry, see: j01.jsonrpc.js
    def j01RegisterCallback(self, cbName, callback, override=False):
        """Register a callback method"""
        if cbName in self.j01CallbackRegistry and not override:
            raise ValueError(
                "callback method %s already exists. "
                "Use j01OverrideCallback instead of j01RegisterCallback "
                "or use override=true" % cbName)
        self.j01CallbackRegistry[cbName] = callback

    def j01OverrideCallback(self, cbName, callback):
        self.j01CallbackRegistry[cbName] = callback

    def j01GetCallback(self, cbName=None, default=None):
        # get callback by name or return default j01RenderContent method
        if default is None:
            default = self.j01RenderContent
        return self.j01CallbackRegistry.get(cbName, default)

    # generic jsonrpc processing
    def doJSONRPCCall(self, url, method, params, onSuccess=None, onError=None):
        # get params from nextURL
        msg = '%s %s' % (method, url)
        self.doAddActivity(msg)
        data = {
            "jsonrpc": "2.0",
            "id": "j01.jsonrpc.testing",
            "method": method,
            "params": params,
            }
        body = json.dumps(data).encode('utf8')
        self.doPostRequest(url, body, 'application/json-rpc')
        # process response (no onSucces, onError support)
        resp = self._response
        data = self.getJSONRPCResult(resp)
        if onSuccess is None:
            # sync request
            return data
        elif data is not None:
            # async request and onSucces is not None
            msg = '%s onSuccess' % onSuccess.__name__
            self.doAddActivity(msg)
            onSuccess(resp)
        elif data is None and onError is not None:
            # error, data is None and onError is not None
            msg = '%s onError' % onError.__name__
            self.doAddActivity(msg)
            onError(resp)

    # global available j01.jsonrpc.js methods
    def j01LoadContent(self, url):
        method = 'j01LoadContent'
        params = self.j01URLToArray(url)
        onSuccess = self.j01RenderContentSuccess
        onError = self.j01RenderContentError
        self.doJSONRPCCall(url, method, params, onSuccess, onError)

    def j01NextURL(self, url):
        msg = 'nextURL %s' % url
        self.doAddActivity(msg)
        self.doRequest('GET', url)

    def j01NextContentURL(self, url):
        msg = 'nextContentURL %s' % url
        self.doAddActivity(msg)
        self.j01LoadContent(url)

    # j01.jsonrpc.js callbacks
    def j01RenderContentSuccess(self, resp, contentTargetExpression=None):
        """Process render content success response

        This method simulates j01RenderContentSuccess method implemented in the
        j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - load content from nextContentURL into dom

        - render content into dom based on contentTargetExpression

        - apply j01PushState based on response.isPushState marker

        """
        if contentTargetExpression is None:
            contentTargetExpression = '#content'
        data = self.getJSONRPCResult(resp)
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        elif data.get('nextContentURL'):
            # load content from nextContentURL
            nextContentURL = data['nextContentURL']
            self.j01NextContentURL(nextContentURL)
        elif data.get('content'):
            # inject content into target
            content = data['content']
            cssSelector = data.get('contentTargetExpression')
            if cssSelector is None:
                cssSelector = contentTargetExpression
            self.doReplaceContent(cssSelector, content)

    def j01RenderContentError(self, resp, errorTargetExpression=None):
        """Process render content error response

        This method simulates j01RenderContentError method implemented in the
        j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - render error message into dom based on errorTargetExpression

        """
        # setup data
        if errorTargetExpression is None:
            errorTargetExpression = '#j01Error'
        rData = self.getJSONRPCError(resp)
        data = rData.get('data', {})
        msg = data.get('i18nMessage')
        if msg is None:
            msg = data.get('message')
        # processing
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        else:
            cssSelector = data.get('errorTargetExpression',
                errorTargetExpression)
            try:
                self.doReplaceContent(cssSelector, msg)
            except ValueError as e:
                if not self.skipDomInjectionError:
                    raise ValueError(
                        "j01RenderContentError error, "
                        "The error message could not get injected into dom "
                        "because the css selector '%s' is not available" % \
                        cssSelector)

    def j01RenderContent(self, resp):
        """Process render content success or error response"""
        data = self.getJSONRPCResult(resp)
        if data is not None:
            self.j01RenderContentSuccess(resp, '#content')
        else:
            self.j01RenderContentError(resp, '#j01Error')

    def setUpJ01Dialog(self, content):
        """Setup j01Dialog and insert into dom with given content"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for inject content")
        # remove previous dialog from dom
        try:
            self.doRemoveElement('#j01DialogHolder')
        except ValueError:
            # dialog not found, just ignore
            pass
        # insert new dialog holder including dialog content
        j01DialogHolder = '<div id="j01DialogHolder">%s</div>' % content
        soup = getBeautifulSoup(self._dom)
        tags = soup.select('body')
        if len(tags) == 1:
            tag = tags[0]
            part = getTagsForContent(j01DialogHolder)
            tag.append(part)
            # store new content in dom, let response as is
            dom = soup.prettify()
            self.setUpDom(dom)
        else:
            raise ValueError("Body tag not found for insert j01Dialog")

    def j01Dialog(self, url):
        """Get dialog by url"""
        method = 'j01Dialog'
        params = self.j01URLToArray(url)
        self.doJSONRPCCall(url, method, params)
        # process sync request response
        resp = self._response
        content = self.getJSONRPCResult(resp)
        if content:
            # setup dialog if content is given otherwise ignore like we do
            # in j01.dialog.js
            self.setUpJ01Dialog(content)
            # add activity
            msg = 'j01Dialog setup %s' % len(content)
            self.doAddActivity(msg)
        else:
            # add activity
            msg = 'j01Dialog missing content -> close'
            self.doAddActivity(msg)

    def j01DialogClose(self, url=None):
        if url is not None:
            msg = 'j01DialogClose %s' % url
        else:
            msg = 'j01DialogClose'
        self.doAddActivity(msg)
        self.doRemoveElement('#j01DialogHolder')
        if url is not None:
            # simply redirect to new page
            self.doRequest('GET', url)
        self.doDocumentReady()

    def j01DialogContent(self, url):
        # get params from nextURL
        method = 'j01LoadContent'
        params = self.j01URLToArray(url)
        onSuccess = self.j01DialogRenderContentSuccess
        onError = self.j01DialogRenderContentError
        self.doJSONRPCCall(url, method, params, onSuccess, onError)

    # j01.dialog.js callbacks and global methods
    def j01DialogRenderContentSuccess(self, resp, contentTargetExpression=None):
        """Process dialog render content success response

        This method simulates j01DialogRenderContentSuccess method implemented
        in the j01.dialog.js javascript. We process the result in the following
        order:

        - close dialog and redirect to nextURL if closeDialog=True in result

        - load content from nextURL into dialog if closeDialog=False in result

        - render result.content into page dom if closeDialog=True

          - use #content as default id if no contentTargetExpression is given

        - close dialog if closeDialog=True

        - render result.content into dialog if closeDialog=False

        """
        if contentTargetExpression is None:
            contentTargetExpression = '#content'
        data = self.getJSONRPCResult(resp)
        nextURL = data.get('nextURL')
        content = data.get('content')
        closeDialog = data.get('closeDialog')
        nextURL = data.get('nextURL')

        # handle error
        if nextURL and closeDialog:
            # close dialog and redirect
            self.doRemoveElement('#j01DialogHolder')
            self.j01NextURL(nextURL)
        elif nextURL:
            # load content from nextURL into dialog
            self.j01DialogContent(nextURL)
        elif content and closeDialog:
            # load content into page dom
            cssSelector = data.get('contentTargetExpression')
            if cssSelector is None:
                cssSelector = contentTargetExpression
            self.doReplaceContent(cssSelector, content)
        elif content:
            # load content into dialog
            cssSelector = '#j01DialogContent'
            self.doReplaceContent(cssSelector, content)
        elif closeDialog:
            # close dialog
            self.doRemoveElement('#j01DialogHolder')
        else:
            # no supported use case
            pass

    def j01DialogRenderContentError(self, resp, errorTargetExpression=None):
        """Process dialog render content error response

        This method simulates j01DialogRenderContentError method implemented in
        the j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - render error message into dom using '#j01DialogContent' css selector

        """
        # setup data
        if errorTargetExpression is None:
            errorTargetExpression = '#j01DialogContent'
        rData = self.getJSONRPCError(resp)
        data = rData.get('data', {})
        msg = data.get('i18nMessage')
        if msg is None:
            msg = data.get('message')
        # processing
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        else:
            # load content into dialog
            cssSelector = '#j01DialogContent'
            self.doReplaceContent(cssSelector, msg)

    def j01DialogRenderContent(self, resp):
        """Process dialog render content success or error response"""
        data = self.getJSONRPCResult(resp)
        if data is not None:
            self.j01DialogRenderContentSuccess(resp, '#content')
        else:
            self.j01DialogRenderContentError(resp)


class JSONRPCMixin(object):
    """Supports j01.jsonrpc button processing"""

    # helper methods
    def j01URLToArray(self, url):
        """Rerturns json-rpc params based on url query or an empty dict"""
        if url:
            parsed = urlparse.urlparse(url)
            query = parsed.query
            data = urlparse.parse_qs(query)
            # convert single items to values
            params = {}
            for k, v in urlparse.parse_qs(query).iteritems():
                if k.endswith(':list'):
                    # marked as list
                    params[k] = v
                elif len(v) > 1:
                    # more then one value, keep list
                    params[k] = v
                else:
                    # single value as string
                    params[k] = v[0]
            return params
        else:
            return {}

    def j01FormToArray(self, form, j01FormHandlerName):
        """Rerturns widget values and j01FormHandlerName as json-rpc params

        NOTE: the j01FormHandlerName is the button name without prefixes.
        """
        params = {}
        for name, value in form._form.submit_fields():
            if name.endswith(':list'):
                # ok that's a list
                values = params.setdefault(name, [])
                values.append(value)
            elif name in params:
                # ok that's a list but no :list marker
                values = params[name]
                if not isinstance(values, list):
                    values = [values]
                values.append(value)
                params[name] = values
            else:
                params[name] = value
        # apply handler (button.__name__) name
        params['j01FormHandlerName'] = j01FormHandlerName
        return params

    def doRemoveElement(self, cssSelector):
        """Remove content from the dom"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for remove element")
        soup = getBeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError("No tag found for remove element")
        elif len(tags) > 1:
            raise ValueError("More then one tag found for remove element")
        else:
            tag = tags[0]
            tag.extract()
            # simply store new content in dom
            dom = soup.prettify()
            self.setUpDom(dom)
            # add activity
            msg = 'DOM remove %s' % cssSelector
            self.doAddActivity(msg)

    def doRemoveContent(self, cssSelector):
        """Remove content from the dom"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for remove content")
        soup = getBeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError("No tag found for remove content")
        elif len(tags) > 1:
            raise ValueError("More then one tag found for remove content")
        else:
            tag = tags[0]
            tag.clear()
            # simply store new content in dom
            dom = soup.prettify()
            self.setUpDom(dom)
            # add activity
            msg = 'DOM empty %s' % cssSelector
            self.doAddActivity(msg)

    def doReplaceContent(self, cssSelector, content):
        """Replace content in dom

        NOTE: this method is used by j01.jsonrpc.testing for inject
        jsonrpc response.

        NOTE: we can't use the last response because it could be partial
        jsonrpc response data. Use the html content stored in our _dom property
        which is always a real html page content

        """
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for inject content")
        soup = getBeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError(
                "No tag found by selector '%s' for insert content" % \
                cssSelector)
        elif len(tags) > 1:
            raise ValueError(
                "More then one tag found by selector '%s' for insert content" \
                % cssSelector)
        else:
            tag = tags[0]
            tag.clear()
            part = getTagsForContent(content)
            tag.append(part)
            # store new content in dom
            # Note: we do NOT store the new content as response. We should
            # implement a html5 browser history which is able to re-call any
            # history based on a given state and some handler methods.
            dom = soup.prettify()
            self.setUpDom(dom)
            msg = 'DOM replace %s %s' % (cssSelector, len(content))
            self.doAddActivity(msg)

    # helper methods
    def getJSONRPCResponse(self, response=None, skipErrors=False):
        # get json data from webtest response
        if response is None:
            response = self._response
        try:
            # Note: the reponse instance can't load json data for non
            # application/json content types e.g. application/x-javascript
            # or application/x-json will fail. Just load them directly from
            # the test body
            data = json.loads(response.testbody)
        except Exception as e:
            if not skipErrors:
                raise e
        try:
            if not data and not skipErrors:
                # raise server response error
                raise interfaces.JSONRPCResponseError(
                    'Missing json response data')
            else:
                return data
        except Exception as e:
            if not skipErrors:
                raise interfaces.JSONRPCResponseError(self.body)

    def getJSONRPCResult(self, response=None, skipErrors=False):
        """Returns response result or None"""
        try:
            data = self.getJSONRPCResponse(response)
            return data.get('result')
        except Exception as e:
            if not skipErrors:
                raise e

    def getJSONRPCError(self, response=None, skipErrors=False):
        """Returns response error or None"""
        try:
            data = self.getJSONRPCResponse(response, skipErrors)
            return data.get('error')
        except Exception as e:
            if not skipErrors:
                raise e


###############################################################################
#
# helper methods mixin

class BrowserHelperMixin(object):
    """Broser testing helper mixin class"""

    def openInBrowser(self, opener=webbrowser.open):
        """Open the given content in a local web browser"""
        if isinstance(self.contents, unicode):
            contents = self.contents.encode('utf8')
        else:
            contents = self.contents
        fd, fname = tempfile.mkstemp('.html')
        os.write(fd, contents)
        os.close(fd)
        return opener("file://%s" % fname)


###############################################################################
#
# test browser

@implementer(interfaces.IBrowser)
class Browser(p01.testbrowser.control.ControlFactoryMixin, JSONRPCMixin,
    JSONRPCCallbackMixin, ActivitiesMixin, HTML5HistoryMixin,
    BrowserHelperMixin, SetattrErrorsMixin):
    """A web browser

    NOTE: the current history implementation stores each response, This is not
    what we should do. We should implement a html5 brwoser history api and only
    store a state with title and url and process them again if we go back.
    This is not as easy as it sounds because the html5 history api stores
    a state which can be any data and javascript handler can get used for
    processing state changes. This means we don't really know what the
    application is doing. Take a look at the j01/jsonrpc/js/j01.jsonrpc.js
    and try to implement a generic concept for support custom state data
    and methods for preocess them see: callbackName, j01PopState and
    j01PushState as a sample concept we need to provide.

    The current implementation uses the following internal response values:

    _response, contains the latest response for any request

    _raw, contains the latest non html response.body

    _dom, contains the latest html response.body

    _title, contains the latest html title from response.body

    Note, this internal private attributes will probably change in the future
    if we implement a better history concept.

    Note: our test browser supports controls outside a form tag. But this
    doesn't mean that they can get submitted without javascript involved.
    We just make sure that we can access controls located outside a form tag
    using a dummy control container called WebTestNonFormControls.

    """

    # hold the initial response content as dom for future ajax injection
    _json = None
    _raw = None
    _wtForms = None
    _title = None
    # private, read and write via _dom
    __dom = None
    # lxml
    _etree = None

    _controls = None
    _counter = 0
    _response = None
    _req_headers = None
    _req_content_type = None

    skipDomWarnings = False
    skipDomErrors = False

    def __init__(self, url=None, wsgi_app=None, getFormControl=None,
        getLinkControl=None, getClickableControl=None, skipDomWarnings=False,
        skipDomErrors=False):
        super(Browser, self).__init__()
        self.timer = PystoneTimer()
        self.raiseHttpErrors = True
        self.handleErrors = True
        if wsgi_app is None:
            proxy = wsgiproxy.proxies.TransparentProxy()
            self.testapp = p01.testbrowser.app.TestApp(proxy)
        else:
            self.testapp = p01.testbrowser.app.TestApp(wsgi_app)
            self.testapp.restricted = True
        self._req_headers = {}
        self._enable_setattr_errors = True
        if getFormControl is not None:
            self.getCustomFormControl = getFormControl
        if getLinkControl is not None:
            self.getCustomLinkControl = getLinkControl
        if getClickableControl is not None:
            self.getCustomClickableControl = getClickableControl
        self.skipDomWarnings = skipDomWarnings
        self.skipDomErrors = skipDomErrors
        self._controls = None
        self.__dom = None
        if url is not None:
            self.doRequest('GET', url)
            self.doDocumentReady()

    @property
    def url(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        if self._response is None:
            return None
        return self.testapp.getRequestUrlWithFragment(self._response)

    @property
    def isHtml(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self._response and 'html' in self._response.content_type

    @property
    def lastRequestPystones(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedPystones

    @property
    def lastRequestSeconds(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedSeconds

    def getTitle(self):
        """Return title from current text/html response"""
        if self.isHtml:
            titles = self._html.find_all('title')
            if titles:
                return self.toStr(titles[0].text)

    @property
    def title(self):
        # get title given from latest text/html response, see doProcessRequest
        return self._title

    def doRedirect(self, url, response):
        """Process redirect without _response caching"""
        # infinite loops protection
        remaining = 100
        while 300 <= response.status_int < 400 and remaining:
            remaining -= 1
            url = urlparse.urljoin(url, response.headers['location'])
            # add activity
            msg = 'redirect %s' % url
            self.doAddActivity(msg)
            # process redirect
            with self._preparedRequest(url) as reqargs:
                response = self.testapp.get(url, **reqargs)
        assert remaining > 0, "redirects chain looks infinite"
        return response

    def doCheckStatus(self):
        # if the headers don't have a status, I suppose there can't be an error
        if 'Status' in self.headers:
            code, msg = self.headers['Status'].split(' ', 1)
            code = int(code)
            if self.raiseHttpErrors and code >= 400:
                raise urllib_request.HTTPError(self.url, code, msg, [], None)

    def getStatus(self):
        # if the headers don't have a status, I suppose there can't be an error
        if 'Status' in self.headers:
            code, msg = self.headers['Status'].split(' ', 1)
            return int(code)
        else:
            # no status header means success
            return 200

    def doResponse(self, response):
        """Set response after processing or history back

        NOTE: this method knows what's to do if we get a json response
        """
        # setup response and make charset available for encoding
        self._response = response
        # reset raw content on each request/response
        self._raw = None
        self._json = None
        if response.body and response.content_type in ['text/html']:
            # store real html content as dom
            dom = self.toStr(response.body)
            self.setUpDom(dom)
        elif response.body:
            # store response body as raw content
            self._raw = response.body
            if response.content_type.endswith((
                '/json', '+json', '/x-json', '/javascript', '/x-javascript')):
                # store response body as json content. Note, the response can't
                # load json data for non 'application/json' headers. just load
                # them here
                self._json = json.loads(response.testbody)

    @property
    def _dom(self):
        return self.__dom

    def setUpDom(self, value):
        self.__dom = value
        # reset parsed forms on dom change
        self._wtForms = None
        self._controls = None
        # set title based on new _dom content
        self._title = self.getTitle()
        # reset lxml etree
        self._etree = None
        self.setUpFormsAndControls()

    # browser content data
    @property
    def _html(self):
        # internal used adhoc parsed dom as BeautifulSoup
        # Note: the lxml is the only parsser whcih will preserve
        # the base url. All other parser will render a wrong base url
        return getTagsForContent(self._dom)

    @property
    def raw(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # returns the raw response.body data
        return self._raw

    @property
    def json(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # returns the encoded response.body data
        return self._json

    @property
    def body(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # return the current (latest) encoded response body
        if self._response is not None:
            return self.toStr(self._response.body)
        else:
            return None

    @property
    def contents(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # return the html stored in the _dom instead of the response.body
        # because the response.body could be partial jsonrpc content
        # NOTE: this means we can't use contents as server response because
        # the jsonrpc respoonse is not returned. Use the raw or json method
        # for access the jsonrpc response.body
        return self._dom

    @property
    def soup(self):
        """Returns the current self._dom as BeautifulSoup"""
        return self._html

    @property
    def headers(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        resptxt = []
        resptxt.append('Status: %s' % self._response.status)
        for h, v in sorted(self._response.headers.items()):
            resptxt.append(str("%s: %s" % (h, v)))

        inp = '\n'.join(resptxt)
        stream = io.BytesIO(inp.encode('latin1'))
        if PYTHON2:
            return httpclient.HTTPMessage(stream)
        else:
            return httpclient.parse_headers(stream)

    @property
    def cookies(self):
        if self.url is None:
            raise RuntimeError("No request found")
        return p01.testbrowser.cookies.Cookies(self.testapp, self.url,
            self._req_headers)

    # request/response api
    def doBeforeRequest(self):
        """Before request/response"""
        # increase control validation counter
        self._counter += 1

    def doAfterRequest(self):
        """After request/response"""
        for k in list(self._req_headers.keys()):
            # remove headers but keep Authorization and Accept-Language
            if k not in ['Authorization', 'Accept-Language']:
                del self._req_headers[k]
        self._req_content_type = None
        # reset skip push state marker
        self.isPushState = None

    @contextmanager
    def _preparedRequest(self, url):
        self.timer.start()
        headers = {}
        if self.url:
            headers['Referer'] = self.url
        if self._req_content_type:
            headers['Content-Type'] = self._req_content_type
        headers['Connection'] = 'close'
        headers['Host'] = urlparse.urlparse(url).netloc
        headers['User-Agent'] = 'Python-urllib/2.7'
        headers.update(self._req_headers)
        extra_environ = {}
        if self.handleErrors:
            extra_environ['paste.throw_errors'] = None
            extra_environ['wsgi.handleErrors'] = True
            headers['X-zope-handle-errors'] = 'True'
        else:
            extra_environ['paste.throw_errors'] = True
            extra_environ['wsgi.handleErrors'] = False
            extra_environ['x-wsgiorg.throw_errors'] = True
            headers.pop('X-zope-handle-errors', None)

        kwargs = {'headers': sorted(headers.items()),
                  'extra_environ': extra_environ,
                  'expect_errors': True}
        self.doBeforeRequest()

        yield kwargs

        self.doAfterRequest()
        self.timer.stop()

    def doProcessRequest(self, url, make_request):
        with self._preparedRequest(url) as reqargs:
            # add previous response to history
            if self._response is not None:
                # only if an initial request was made
                self.j01PushState(self._response, self._dom, self._title)
            # process request
            resp = make_request(reqargs)
            # process redirect if any
            resp = self.doRedirect(url, resp)
            # apply response
            self.doResponse(resp)
            # check status
            self.doCheckStatus()
            # add activity
            activity = RequestActivity(resp, self._dom, self._title)
            self.doAddActivity(activity)

    # def addHeader(self, key, value):
    #     """See p01.testbrowser.interfaces.IBrowser"""
    #     if (self.url and
    #         key.lower() in ('cookie', 'cookie2') and
    #         self.cookies.header):
    #         raise ValueError('cookies are already set in `cookies` attribute')
    #     self._req_headers[key] = value

    # def addHeader(self, key, value):
    #     """See p01.testbrowser.interfaces.IBrowser"""
    #     if (self.url and
    #         key.lower() in ('cookie', 'cookie2') and
    #         self.cookies.header):
    #         raise ValueError('cookies are already set in `cookies` attribute')
    #     key = _wsgi_header_name(key)
    #     value = _wsgi_header_value(value)
    #     self._req_headers[str(key)] = str(value)

    def addHeader(self, key, value):
        """See p01.testbrowser.interfaces.IBrowser"""
        if (self.url and
            key.lower() in ('cookie', 'cookie2') and
            self.cookies.header):
            raise ValueError('cookies are already set in `cookies` attribute')
        if isinstance(key, bytes):
            key = key.decode('latin-1')
        if isinstance(value, bytes):
            value = value.decode('latin-1')
        self._req_headers[str(key)] = str(value)

    def doRequest(self, method, url, data=None, headers=None):
        """Proces a request based on given request method"""
        method = method.upper()
        url = self._absoluteUrl(url)
        if headers is not None:
            for k, v in headers.items():
                self.addHeader(k, v)
        if method == 'GET':
            make_request = lambda args: self.testapp.get(url, **args)
        elif method == 'HEAD':
            make_request = lambda args: self.testapp.head(url, **args)
        elif method == 'OPTIONS':
            make_request = lambda args: self.testapp.options(url, **args)
        elif method == 'POST':
            assert data is not None
            make_request = lambda args: self.testapp.post(url, data, **args)
        elif method == 'PATCH':
            assert data is not None
            make_request = lambda args: self.testapp.patch(url, data, **args)
        elif method == 'PUT':
            assert data is not None
            make_request = lambda args: self.testapp.put(url, data, **args)
        else:
            if data is None:
                params = webtest.utils.NoDefault
            else:
                params = data
            make_request = lambda args: self.testapp._gen_request(method, url,
                params, **args)
        self.doProcessRequest(url, make_request)

    def doGetRequest(self, url):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.doRequest('GET', url)

    def doPostRequest(self, url, data, content_type=None):
        if content_type is not None:
            self._req_content_type = content_type
        self.doRequest('POST', url, data)

    def request(self, method, url, data=None, headers=None):
        """Generic request handling including document ready handling"""
        msg = 'request %s %s' % (method.upper(), url)
        self.doAddActivity(msg)
        self.doRequest(method, url, data=data, headers=headers)
        self.doDocumentReady()

    def get(self, url):
        """GET request including document ready handling"""
        msg = 'get %s' % url
        self.doAddActivity(msg)
        self.doGetRequest(url)
        self.doDocumentReady()

    def post(self, url, data, content_type=None):
        """POST request including document ready handling"""
        msg = 'post %s' % url
        self.doAddActivity(msg)
        self.doPostRequest(url, data, content_type=content_type)
        self.doDocumentReady()

    def open(self, url, data=None):
        """Generic GET or POST request depending on given data including
        document ready handling
        """
        msg = 'open %s' % url
        self.doAddActivity(msg)
        if data is not None:
            method = 'POST'
        else:
            method = 'GET'
        self.doRequest(method, url, data)
        self.doDocumentReady()

    def reload(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        msg = 'reload %s' % self.url
        self.doAddActivity(msg)
        if self._response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No URL has yet been .open()ed")
        req = self._response.request
        with self._preparedRequest(self.url):
            resp = self.testapp.request(req)
            self.doResponse(resp)
        self.doDocumentReady()

    def goBack(self, count=1):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.history.back(count)

    def goForward(self, count=1):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.history.go(count)

    # links
    def getLink(self, text=None, url=None, id=None, index=0):
        """See p01.testbrowser.interfaces.IBrowser"""
        qa = 'a' if id is None else 'a#%s' % id
        qarea = 'area' if id is None else 'area#%s' % id
        html = self._html
        links = html.select(qa)
        links.extend(html.select(qarea))

        # find matching elements
        matching = []
        for elem in links:
            if (isMatching(elem.text, text) and
                isMatching(elem.get('href', ''), url)):
                matching.append(elem)

        if index >= len(matching):
            raise p01.testbrowser.exceptions.LinkNotFoundError()
        elem = matching[index]

        # setup link control
        link = self.getCustomLinkControl(elem)
        if link is None:
            link = self.getJSONRPCLinkControl(elem)
        if link is None:
            link = p01.testbrowser.control.Link(self, elem)
        return link

    def follow(self, *args, **kw):
        """Select a link and follow it."""
        self.getLink(*args, **kw).click()

    # clickable
    def getClickable(self, text=None, url=None, id=None, index=0):
        """See p01.testbrowser.interfaces.IBrowser"""
        # filter by id
        html = self._html
        if id is not None:
            selector = '#%s' % id
            elements = html.select(selector)
        else:
            elements = html

        # lookup clickables
        clickables = []
        for elem in elements:
            # check custom clickable control
            clickable = self.getCustomClickableControl(elem, text, url)
            if clickable is not None:
                clickables.append(clickable)
                continue
            # check available jsonrpc clickable control
            clickable = self.getJSONRPCClickableControl(elem, text, url)
            if clickable is not None:
                clickables.append(clickable)

        # return by index
        if index >= len(clickables):
            raise p01.testbrowser.exceptions.LinkNotFoundError()
        return clickables[index]

    # forms/controls
    def getForm(self, id=None, name=None, action=None, index=None):
        """See p01.testbrowser.interfaces.IBrowser"""
        zeroOrOne([id, name, action], '"id", "name", and "action"')
        forms = []
        wtForms = self.getWebTestForms()
        for wtForm in wtForms:
            if not wtForm.html.form:
                # that's our dummy control container form we do not allow to
                # get them as form
                continue
            if ((id is not None and wtForm.id == id) or
                (name is not None and wtForm.html.form.get('name') == name) or
                (action is not None and re.search(action, wtForm.action)) or
                id == name == action == None):
                forms.append(wtForm)
        if index is None and not any([id, name, action]):
            if len(forms) == 1:
                index = 0
            else:
                raise ValueError(
                    'if no other arguments are given, index is required.')
        wtForm = disambiguate(forms, '', index)
        return p01.testbrowser.control.Form(self, wtForm)

    def getControl(self, label=None, name=None, index=None):
        """See p01.testbrowser.interfaces.IBrowser"""
        wtForms = self.getWebTestForms()
        intermediate, msg, available = self._getAllControls(label, name,
            wtForms, include_subcontrols=True)
        control = disambiguate(intermediate, msg,
            index, controlFormTupleRepr, available)
        return control

    def getControls(self, render=False, prettify=False, asDict=False,
        skipSubControls=False):
        """Return all available controls for current _dom"""
        wtForms = self.getWebTestForms()
        include_subcontrols = not skipSubControls
        controls = self._findAllControls(wtForms, include_subcontrols)
        if render:
            for entry in controls:
                print(entry.render(prettify=prettify))
        elif asDict:
            return dict([(control.name, control) for control in controls])
        else:
            return controls

    def hasControl(self, label=None, name=None, index=None):
        """Knows if a control is available without to print disambiguate"""
        wtForms = self.getWebTestForms()
        intermediate, msg, available = self._getAllControls(label, name,
            wtForms, include_subcontrols=True)
        if intermediate:
            return True
        else:
            return False

    # don't offer this method as long as we dump the control to dom on any
    # control value change and setup new control instances. Otherwise the
    # controls in the dict get outdated very quickly. Wich means you will
    # better call getControl anytime you need a control. You can simply do
    # gc = browser.getControl and use such a shortcut function pointer
    # or
    # def getControlsAsDict(self, skipSubControls=True):
    #     """Get controls as dict with controll name as key""
    #     return self.getControls(render=False, prettify=False, asDict=True,
    #         skipSubControls=skipSubControls)

    def getControlsOutsideForm(self, render=False, prettify=False):
        """Return all available controls outside a form"""
        # first ensure forms and get our dummy form
        if self._wtForms is None:
            self.setUpFormsAndControls()
        wtForms = [self._wtForms[None]]
        include_subcontrols = True
        controls = self._findAllControls(wtForms, include_subcontrols)
        if render:
            for entry in controls:
                print(entry.render(prettify=prettify))
        else:
            return controls

    def getLinks(self, render=False, prettify=False):
        """Return all available links for current _dom"""
        # include a and area elements
        qa = 'a'
        qarea = 'area'
        html = self._html
        links = self.soup.select(qa)
        links.extend(html.select(qarea))
        controls = []
        for elem in links:
            # setup link control
            ctrl = self.getCustomLinkControl(elem)
            if ctrl is None:
                ctrl = self.getJSONRPCLinkControl(elem)
            if ctrl is None:
                ctrl = p01.testbrowser.control.Link(self, elem)
            controls.append(ctrl)
        if render:
            for entry in controls:
                print(entry.render(prettify=prettify))
        else:
            return controls

    @property
    def controls(self):
        return self.getControls(render=False, prettify=False)

    # internal control query helpers
    def _getAllControls(self, label, name, wtForms, include_subcontrols=False):
        p01.testbrowser.control.onlyOne([label, name], '"label" and "name"')
        wtForms = list(wtForms) # might be an iterator, and we need to iterate twice
        available = None
        if label is not None:
            res = self._findByLabel(label, wtForms, include_subcontrols)
            msg = 'label %r' % label
        elif name is not None:
            include_subcontrols = False
            res = self._findByName(name, wtForms)
            msg = 'name %r' % name
        if not res:
            available = list(self._findAllControls(wtForms, include_subcontrols))
        return res, msg, available

    def _findByLabel(self, label, wtForms, include_subcontrols=False):
        label = ' '.join(label.split())
        matches = re.compile(r'(^|\b|\W)%s(\b|\W|$)' % re.escape(label)).search
        found = []
        for wtcontrol in self._findAllControls(wtForms, include_subcontrols):
            for l in wtcontrol.labels:
                if matches(l):
                    found.append(wtcontrol)
                    break
        return found

    def _findByName(self, name, wtForms):
        return [c for c in self._findAllControls(wtForms) if c.name == name]

    def _findAllControls(self, wtForms, include_subcontrols=False):
        res = []
        for f in wtForms:
            controls = [c for c, subcontrol in self._controls[f]
                        if not subcontrol or include_subcontrols]
            res.extend(controls)
        return res

    # form/control setup
    def _getControlElements(self, form=None):
        # Unfortunately, webtest will remove all 'name' attributes from
        # form.html after parsing. But we need them (at least to locate labels
        # for radio buttons). So we are forced to reparse part of html, to
        # extract elements.
        soup = getBeautifulSoup(form.text)
        tags = ('input', 'select', 'textarea', 'button')
        return soup.find_all(tags)

    def setUpFormsAndControls(self):
        """Setup webtest forms in the order they appear in the dom"""
        # self._wtForms = collections.OrderedDict()
        self._wtForms = {}
        # form_texts = [str(f) for f in self._html('form')]
        soup = getBeautifulSoup(self._dom)
        form_texts = [str(f) for f in soup('form')]
        for i, text in enumerate(form_texts):
            # ATTENTION: the form uses self._response, but luckily the
            # response is only used for submit the form with response.goto
            # But we don't use form.goto for submit the form
            # form = WebTestForm(self._response, text, 'html.parser')
            form = WebTestForm(self._response, text, 'lxml')
            #form = WebTestForm(self._response, text)
            # add the form with enumerated integer as key
            self._wtForms[i] = form
            if form.id:
                # also add the same form reference with it's id as key
                self._wtForms[form.id] = form
        # add dummy control container for controls outside a form
        text = self._dom
        self._wtForms[None] = WebTestNonFormControls(self._response, text)

        # setup controls
        self._controls = {}
        # use unique forms
        for f in self.getWebTestForms():
            fc = []
            allelems = self._getControlElements(f)
            already_processed = set()
            for cname, wtcontrol in f.field_order:
                # we need to group checkboxes by name, but leave
                # the other controls in the original order,
                # even if the name repeats
                if isinstance(wtcontrol, webtest.forms.Checkbox):
                    if cname in already_processed:
                        continue
                    already_processed.add(cname)
                    wtcontrols = f.fields[cname]
                else:
                    wtcontrols = [wtcontrol]
                for c in self.getFormControls(cname, wtcontrols, allelems):
                    fc.append((c, False))
                    for subcontrol in c.controls:
                        fc.append((subcontrol, True))
            self._controls[f] = fc

    def getWebTestForms(self):
        if self._wtForms is None:
            self.setUpFormsAndControls()
        # only return the forms onece, we just use the forms with integer as
        # keys and append our None form control wrapper
        idxkeys = [k for k in self._wtForms.keys() if isinstance(k, int)]
        forms = [self._wtForms[k] for k in sorted(idxkeys)]
        forms.append(self._wtForms[None])
        return forms

    # render controls back to dom
    def findElementInDomForControl(self, soup, control):
        """Find releated control element in dom"""
        # get soup based on current dom sting
        # find current control element in new dom
        tagName = control.tag
        query = control.getDomQueryArguments()
        tags = soup.find_all(tagName, query)
        if len(tags) == 1:
            # only return if we find the right element, more then one means the
            # query was not selective enough
            return tags[0]

    def findElementInDomForParentControl(self, soup, control):
        # find current control element in new dom
        tagName = control.tag
        query = control.getDomQueryArguments()
        tag = None
        # find the element based on the parent element
        pctr = getattr(control, '_parent', None)
        if pctr is not None:
            pquery = pctr.getDomQueryArguments()
            pTag = soup.find(pctr.tag, pquery)
            if pTag is not None:
                tag = pTag.find(tagName, query)
                if tag is None:
                    # ok, tag not found, try to find the sub tag based on
                    # it's control element index
                    dsl = [c.asDomString for c in control._parent.controls]
                    try:
                        idx = dsl.index(control.asDomString)
                        # get the element with the same position from the
                        # dom element, but first, limit the elements to
                        # only the relevant tags
                        pTagElements = pTag.find_all(tagName)
                        tag = pTagElements[idx]
                    except ValueError:
                        # index error
                        pass
        return tag

    def dumpControlToDom(self, control):
        """Dump controls back to dom

        This will ensure, that we allways provide a corret dom. This is nice
        because if doesn't confuse while the controles are not just a virtual
        layer with different values anymore.


        But the more important reason for this concept is, that if we update the
        form with a jsonrpc request, the controls will get invalidated and
        parsed again after each json.rpc request. This means we should loose
        pre set control values which didn't get replaced by the repsonse.

        Note: this concept is not required for non json.rpc request and also
        not for json-rpc request whcih don't only replace partial form parts.
        This means you can probably supress the warngin and error message for
        testing your page.

        """
        # get soup based on current dom sting
        soup = getBeautifulSoup(self._dom, 'lxml')
        tagName = control.tag
        tag = None
        if tagName in ['option']:
            tag = self.findElementInDomForParentControl(soup, control)
        if tag is None:
            # get element from dom for given control
            tag = self.findElementInDomForControl(soup, control)
        if tag is not None:
            # replace dom element with given control including all values
            # use a html parser and prevent to render single closed tags for
            # empty elements, that's usefull for texarea, pre p tags etc.
            #
            # XXX: implement control.asTagElement and do this in Control
            # instead of here
            cTag = getTagsForContent(control.asDomString)
            if tagName == 'textarea' and len(cTag.textarea.contents) > 0:
                for child in list(cTag.textarea.contents):
                    # extract child
                    child.extract()
                # insert real textarea content based on value
                plain = NavigableString(control.value)
                cTag.textarea.insert(0, plain)
            tag.replace_with(cTag)
            # replace control element
            # dump to _dom string
            dom = soup.prettify()
            self.setUpDom(dom)
        else:
            if not self.skipDomWarnings:
                print(DOM_WARNING_MESSAGE)
            if not self.skipDomErrors:
                raise ValueError(
                    "Dom element for tag "
                    "%s "
                    "not found for insert into dom. "
                    "You can supress this warning and error with the test "
                    "Browser options skipDomWarnings and skipDomErrors" % \
                    control)

    # internal request/response helper methods
    def _getBaseUrl(self):
        # Look for <base href> tag and use it as base, if it exists
        url = self._response.request.url
        if b"<base" not in self._response.body:
            return url

        # we suspect there is a base tag in body, try to find href there
        html = self._html
        if not html.head:
            return url
        base = html.head.base
        if not base:
            return url
        return base['href'] or url

    def _absoluteUrl(self, url):
        absolute = url.startswith('http://') or url.startswith('https://')
        if absolute:
            return str(url)

        if self._response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Can't fetch relative reference: not viewing any document")

        return str(urlparse.urljoin(self._getBaseUrl(), url))

    def toStr(self, s):
        """Convert possibly unicode object to native string using response
        charset"""
        if not self._response.charset:
            return s
        if s is None:
            return None
        if PYTHON2 and not isinstance(s, bytes):
            return s.encode(self._response.charset)
        if not PYTHON2 and isinstance(s, bytes):
            return s.decode(self._response.charset)
        return s

    # lxml API
    @property
    def etree(self):
        if self._etree is not None:
            return self._etree
        if self._dom is not None:
            encoding = 'utf-8'
            parser = lxml.etree.HTMLParser(encoding=encoding,
                remove_blank_text=True, remove_comments=True, recover=True)
            self._etree = lxml.etree.fromstring(self._dom, parser=parser)
        return self._etree

    # xpath
    def extract(self, xpath, strip=False, rv=False):
        """Extract content from current _dom by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        txt = xs.extract(xpath, strip=strip)
        txt = '\n'.join([x.rstrip() for x in txt.splitlines()
                         if x.rstrip().replace('\n', '')])
        if rv:
            return txt
        else:
            print(txt)

    # text
    def asText(self, xpath='.//body', rv=False):
        """Output current _dom as text by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        res = []
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        for item in xs.xpath(xpath):
            res.append(getNodeText(item))
        txt = '\n'.join(res)
        while '\n\n' in txt:
            txt = txt.replace('\n\n', '\n')
        txt = '\n'.join([x.strip() for x in txt.splitlines()
                         if x.strip().replace('\n', '')])
        if rv:
            return txt
        else:
            print(txt)

    def asTextByCSSClass(self, classes, rv=False):
        """Returns the elements as text selected by css classes"""
        txt = ''
        for cls in classes:
            xp = ("descendant-or-self::div[@class and "
                  "contains(concat(' ', normalize-space(@class), ' '), "
                  "' %s ')]" % cls)
            txt += self.asText(xpath=xp, rv=True)
        if rv:
            return txt
        else:
            print(txt)

    def asPlainText(self, xpath=None, rv=False, **kw):
        """Output current _dom as text by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        if xpath is not None:
            xs = p01.testbrowser.xpath.getXPathSelector(content)
            content = xs.extract(xpath)
        content = content.decode('utf8')
        txt = p01.testbrowser.html2text.html2text(content, **kw)
        txt = '\n'.join([x.rstrip() for x in txt.splitlines()])
        txt = txt.replace('\n\n', '\n')
        if rv:
            return txt
        else:
            print(txt)

    def asTable(self, xpath='.//table'):
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        node = xs.xpath(xpath)
        if isinstance(node, (list, tuple)):
            for item in node:
                print("Table:")
                rows = item.xpath('.//tr')
                for row in rows:
                    print(map(getNodeText, row.xpath('./th|./td')))
        else:
            rows = node.xpath('.//tr')
            for row in rows:
                print(map(getNodeText, row.xpath('./th|./td')))

    # node 2 string
    def node2String(self, xpath, strip=False):
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        res = []
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        for node in xs.xpath(xpath):
            node2String(node, res)
        print('\n'.join(res))

    def form2String(self, selector=None):
        if selector is None:
            selector = [
                # widgets
                './/input[@type="text"]',
                './/input[@type="email"]',
                './/input[@type="url"]',
                './/input[@type="password"]',
                './/input[@type="date"]',
                './/input[@type="datetime"]',
                './/input[@type="datetime-local"]',
                './/input[@type="hidden"]',
                './/select',
                './/textarea',
                # status
                './/div[@class="status"]',
                # buttons
                './/input[@type="submit"]',
                './/input[@type="button"]',
                './/input[@type="reset"]',
                './/button',
                ]
        if isinstance(selector, list):
            selector = '|'.join(selector)
        self.node2String(selector)

    def widget2String(self, selector=None):
        if selector is None:
            selector = [
                './/input[@type="submit"]',
                './/input[@type="text"]',
                './/input[@type="password"]',
                './/input[@type="date"]',
                './/input[@type="hidden"]',
                './/select',
                './/textarea',
                ]
        if isinstance(selector, list):
            selector = '|'.join(selector)
        self.node2String(selector)

    def button2String(self, selector=None):
        if selector is None:
            selector = [
                './/input[@type="submit"]',
                './/input[@type="button"]',
                './/input[@type="reset"]',
                './/button',
                ]
        if isinstance(selector, list):
            selector = '|'.join(selector)
        self.node2String(selector)

    def link2String(self, selector=None):
        if selector is None:
            selector = ['.//a',]
        if isinstance(selector, list):
            selector = '|'.join(selector)
        self.node2String(selector)

    # grep
    def grep(self, pattern, rv=False):
        P = re.compile(pattern)
        res = []
        for line in self._dom.splitlines():
            if P.search(line):
                  res.append(line)
        txt = ''.join(res)
        if rv:
            return txt
        else:
            print(txt)

    def __contains__(self, value):
        return value in self.contents

    def __repr__(self):
        return '<%s url:%s>' % (self.__class__.__name__, self.url)


def node2String(node, res):
    if isinstance(node, (list, tuple)):
        for item in node:
            node2String(item, res)
    else:
        txt = lxml.etree.tostring(node, pretty_print=True)
        txt = txt.strip()
        while '\n\n' in txt:
            txt = txt.replace('\n\n', '\n')
        if txt:
            res.append(txt)


def getNodeText(node, addTitle=False):
    if isinstance(node, (list, tuple)):
        tags = [getNodeText(child, addTitle).strip() for child in node]
        return '\n'.join()
    text = []
    if node is None:
        return None
    if node.tag == 'script':
        return ''
    if node.tag == 'br':
        return '\n'
    if node.tag == 'input':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        if node.get('type') == 'checkbox':
            chk = node.get('checked')
            return title +('[x]' if chk is not None else '[ ]')
        if node.get('type') == 'hidden':
            return ''
        else:
            return '%s[%s]' % (title, node.get('value') or '')
    if node.tag == 'textarea':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
            text.append(title)
    if node.tag == 'select':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        option = node.find('option[@selected]')
        return '%s[%s]' % (title, option.text if option is not None else '[    ]')
    if node.tag == 'li':
        text.append('*')

    if node.text:
        text.append(node.text)
    for n, child in enumerate(node):
        s = getNodeText(child, addTitle)
        if s:
            text.append(s)
        if child.tail:
            text.append(child.tail)
    text = ' '.join(text).strip()
    # 'foo<br>bar' ends up as 'foo \nbar' due to the algorithm used above
    text = text.replace(' \n', '\n').replace('\n ', '\n')
    if u'\xA0' in text:
        # don't just .replace, that'll sprinkle my tests with u''
        text = text.replace(u'\xA0', ' ') # nbsp -> space
    if node.tag == 'li':
        text += '\n'
    return text
