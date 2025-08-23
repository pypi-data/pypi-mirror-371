# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id:$
"""
from __future__ import unicode_literals, absolute_import, print_function

__docformat__ = "reStructuredText"

import sys
import unittest
from io import BytesIO  # Py2/3 vorhanden

import zope.component
from zope.publisher.base import DefaultPublication
from zope.publisher.http import HTTPCharsets

from p01.jsonrpc.publisher import JSONRPCRequest


class Publication(DefaultPublication):
    require_docstrings = 0


class TestJSONRPCRequest(JSONRPCRequest, HTTPCharsets):
    """Make sure that our request also implements IHTTPCharsets, so that we do
    not need to register any adapters."""

    def __init__(self, *args, **kw):
        self.request = self
        JSONRPCRequest.__init__(self, *args, **kw)


class PositionalTestCall:
    def __init__(self):
        self.body = '{"jsonrpc":"2.0","id":"httpReq","method":"positional","params":["aaa","bbb"]}'
        self.headers = []


class NamedTestCall:
    def __init__(self):
        self.body = '{"jsonrpc":"2.0","id":"httpReq","method":"named","params":{"kw1":"aaa","kw2":"bbb"}}'
        self.headers = []


class JSONRPCTests(unittest.TestCase):
    """The only thing different to HTTP is the input processing; so there
       is no need to redo all the HTTP tests again.
    """

    _testEnv = {
        'PATH_INFO': '/folder/item2/view/',
        'QUERY_STRING': '',
        'SERVER_URL': 'http://foobar.com',
        'HTTP_HOST': 'foobar.com',
        'CONTENT_LENGTH': '0',
        'REQUEST_METHOD': 'POST',
        'HTTP_AUTHORIZATION': 'Should be in accessible',
        'GATEWAY_INTERFACE': 'TestFooInterface/1.0',
        'HTTP_OFF_THE_WALL': "Spam 'n eggs",
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33',
        # optionale, aber oft hilfreiche Defaults:
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
    }

    def setUp(self):
        super(JSONRPCTests, self).setUp()

        class AppRoot(object):
            pass

        class Folder(object):
            pass

        class Item(object):

            def __call__(self, a, b):
                return "%s, %s" % (a, b)

            def doit(self, a, b):
                return 'do something %s %s' % (a, b)

        class View(object):

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def positional(self, a, b):
                return "Parameter: a; type: %s; value: %s" % (
                    type(a).__name__, a)

            def named(self, kw1=None, kw2=None):
                kw1 = self.request.get('kw1', kw1)
                kw2 = self.request.get('kw2', kw2)
                return ("Keyword: kw1; type: %s; value: %s] "
                        "Keyword: kw2; type: %s; value: %s]") % (
                    type(kw1).__name__, kw1, type(kw2).__name__, kw2)

        class Item2(object):
            request = None

            @property
            def view(self):
                return View(self, self.request)

        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()
        self.app.folder.item2 = Item2()
        # zope.component.provideUtility(JSONReader(), IJSONReader)

    def _createRequest(self, extra_env=None, body=""):
        if extra_env is None:
            extra_env = {}
        env = self._testEnv.copy()
        env.update(extra_env)

        # Body IMMER als bytes an den Request geben
        raw = body.body
        if isinstance(raw, bytes):
            data = raw
        else:
            # raw ist ein str → zu UTF-8 Bytes konvertieren
            data = raw.encode('utf-8')

        if data:
            env['CONTENT_LENGTH'] = str(len(data))

        publication = Publication(self.app)
        instream = BytesIO(data)
        request = TestJSONRPCRequest(instream, env)
        request.setPublication(publication)
        return request

    def testProcessInput(self):
        req = self._createRequest({}, PositionalTestCall())
        self.app.folder.item2.request = req
        req.processInputs()
        # Werte prüfen (Typen: Py2 unicode, Py3 str)
        self.assertEqual(tuple(req._args), (u'aaa', u'bbb'))
        self.assertEqual(tuple(req._path_suffix), ('positional',))

    def testPositional(self):
        req = self._createRequest({}, PositionalTestCall())
        self.app.folder.item2.request = req
        req.processInputs()
        action = req.traverse(self.app)
        expected_typename = 'unicode' if sys.version_info[0] == 2 else 'str'
        self.assertEqual(
            action(*req._args),
            'Parameter: a; type: %s; value: aaa' % expected_typename
        )

    def testKeyword(self):
        req = self._createRequest({}, NamedTestCall())
        self.app.folder.item2.request = req
        req.processInputs()
        action = req.traverse(self.app)
        expected_typename = 'unicode' if sys.version_info[0] == 2 else 'str'
        self.assertEqual(
            action(*req._args, **req.form),
            u'Keyword: kw1; type: %s; value: aaa] '
            u'Keyword: kw2; type: %s; value: bbb]' % (
                expected_typename, expected_typename
            )
        )

    def testJSONRPCMode(self):
        req = self._createRequest({}, PositionalTestCall())
        self.app.folder.item2.request = req
        req.processInputs()
        self.assertEqual(req['JSONRPC_MODE'], True)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(JSONRPCTests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
