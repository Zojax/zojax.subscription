##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
""" zojax.subscription tests

$Id$
"""
import os, unittest, doctest
from persistent import Persistent
from zope import interface, component
from zope.app.testing import functional
from zope.app.component.hooks import setSite
from zope.app.container.contained import Contained
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds


zojaxSubscriptionLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxSubscriptionLayer', allow_teardown=True)

class Content(Persistent, Contained):
    pass


def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxSubscriptionLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        setSite(root)
        sm = root.getSiteManager()

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def test_suite():
    return unittest.TestSuite((
            FunctionalDocFileSuite("tests.txt"),
            FunctionalDocFileSuite("catalog.txt"),
            FunctionalDocFileSuite("testbrowser.txt"),
            ))
