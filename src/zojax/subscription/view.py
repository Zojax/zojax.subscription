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
"""

$Id$
"""
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.batching.batch import Batch

from interfaces import _


class SubscriptionsView(object):

    unknown = _('Unknown')

    def update(self):
        results = self.context.search(visibility=None)
        list(removeAllProxies(self.context).catalog.getIndexes())

        self.batch = Batch(
            results, size=20,
            context=self.context, request=self.request)

        self.auth = getUtility(IAuthentication)

    def getInfo(self, record):
        info = {'type': record.type,
                'object': self.unknown,
                'objectUrl': None,
                'principal': self.unknown}

        object = record.object
        if object is not None:
            info['object'] = getattr(object, 'title', object.__name__)
            try:
                info['objectUrl'] = u'%s/'%absoluteURL(object, self.request)
            except:
                pass

        if record.principal:
            try:
                principal = self.auth.getPrincipal(record.principal)
                info['principal'] = principal.title
            except PrincipalLookupError:
                pass

        return info
