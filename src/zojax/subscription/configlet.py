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
import BTrees, random

from zope import interface, event, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.app.intid.interfaces import IIntIds, IIntIdRemovedEvent

from catalog import SubscriptionsCatalog
from interfaces import ISubscriptions
from interfaces import ISubscriptionAddedEvent, ISubscriptionRemovedEvent


class SubscriptionsConfiglet(object):
    interface.implements(ISubscriptions)

    family = BTrees.family32

    _v_nextid = None
    _randrange = random.randrange

    @property
    def subscriptions(self):
        data = self.data.get('subscriptions')
        if data is None:
            data = self.family.IO.BTree()
            self.data['subscriptions'] = data
        return data

    @property
    def catalog(self):
        catalog = self.data.get('catalog')
        if catalog is None:
            catalog = SubscriptionsCatalog()
            self.data['catalog'] = catalog
        return catalog

    def _generateId(self):
        subscriptions = self.subscriptions

        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, self.family.maxint)

            id = self._v_nextid
            self._v_nextid += 1

            if id not in subscriptions:
                return id

            self._v_nextid = None

    def search(self, **kw):
        return self.catalog.search(**kw)

    def principalSubscriptions(self, principal):
        return self.catalog.search(
            principal={'any_of': (principal,)}, visibility=None)

    def unsubscribePrincipal(self, principal, id):
        subscription = self.subscriptions.get(id)
        if subscription is not None and subscription.principal == principal:
            self.remove(id)

    def objectSubscriptions(self, object):
        return self.catalog.search(object=object, visibility=None)

    def updateObjectSubscriptions(self, object):
        catalog = self.catalog

        for subscription in catalog.search(object=object, visibility=None):
            catalog.index_doc(subscription.id, subscription)

    def getObject(self, id):
        return self.subscriptions[id]

    def add(self, object, subscription):
        oid = getUtility(IIntIds).queryId(removeAllProxies(object))
        if oid is None:
            return

        subscription.id = self._generateId()
        subscription.oid = oid

        self.subscriptions[subscription.id] = subscription
        self.catalog.index_doc(subscription.id, subscription)

        event.notify(SubscriptionAddedEvent(object, subscription))

    def remove(self, id):
        subscriptions = self.subscriptions

        subscription = subscriptions[id]
        event.notify(SubscriptionRemovedEvent(subscription.object,subscription))

        self.catalog.unindex_doc(id)
        del subscriptions[id]

    def removeObject(self, object):
        catalog = self.catalog
        subscriptions = self.subscriptions

        for id in self.catalog.search(object, visibility=None).uids:
            event.notify(SubscriptionRemovedEvent(object, subscriptions[id]))

            catalog.unindex_doc(id)
            del subscriptions[id]

    def removeSubscription(self, object, principal, type):
        catalog = self.catalog
        subscriptions = self.subscriptions

        for id in self.catalog.search(
            object, principal = {'any_of': (principal,)},
            type = {'any_of': (type,)}, visibility=None).uids:

            event.notify(SubscriptionRemovedEvent(object, subscriptions[id]))
            catalog.unindex_doc(id)
            del subscriptions[id]


class SubscriptionEvent(object):

    def __init__(self, object, subscription):
        self.object = object
        self.subscription = subscription


class SubscriptionAddedEvent(SubscriptionEvent):
    interface.implements(ISubscriptionAddedEvent)


class SubscriptionRemovedEvent(SubscriptionEvent):
    interface.implements(ISubscriptionRemovedEvent)


@component.adapter(IIntIdRemovedEvent)
def objectRemovedHandler(ev):
    removeAllProxies(getUtility(ISubscriptions)).removeObject(ev.object)
