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
from BTrees.IFBTree import IFBTree

from zope import component, interface, event
from zope.proxy import removeAllProxies
from zope.component import getUtility, getAdapter, getAdapters
from zope.app.catalog import catalog
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zc.catalog.catalogindex import SetIndex, ValueIndex

from zojax.security.utils import getPrincipal, checkPermissionForPrincipal
from zojax.catalog.result import ResultSet, ReverseResultSet
from zojax.catalog.index import DateTimeValueIndex
from zojax.catalog.interfaces import ISortable, ICatalogIndexFactory

from interfaces import ISubscriptions, ISubscriptionsCatalog


class SubscriptionsCatalog(catalog.Catalog):
    interface.implements(ISubscriptionsCatalog)

    def createIndex(self, name, factory):
        index = factory()
        event.notify(ObjectCreatedEvent(index))
        self[name] = index

        return self[name]

    def getIndex(self, indexId):
        if indexId in self:
            return self[indexId]

        return self.createIndex(
            indexId, getAdapter(self, ICatalogIndexFactory, indexId))

    def getIndexes(self):
        names = []

        for index in self.values():
            names.append(removeAllProxies(index.__name__))
            yield index

        for name, indexFactory in getAdapters((self,), ICatalogIndexFactory):
            if name not in names:
                yield self.createIndex(name, indexFactory)

    def clear(self):
        for index in self.getIndexes():
            index.clear()

    def index_doc(self, docid, texts):
        for index in self.getIndexes():
            index.index_doc(docid, texts)

    def unindex_doc(self, docid):
        for index in self.getIndexes():
            index.unindex_doc(docid)

    def updateIndexes(self):
        indexes = list(self.getIndexes())

        for uid, obj in self._visitSublocations():
            for index in indexes:
                index.index_doc(uid, obj)

    def _visitSublocations(self):
        configlet = getUtility(ISubscriptions)

        for uid, subscription in \
                removeAllProxies(configlet).subscriptions.items():
            yield uid, subscription

    def search(self, object=None, contexts=(), visibility=True, **kw):
        ids = getUtility(IIntIds)

        query = dict(kw)

        # subscriptions for object
        if object is not None:
            if type(object) is not type({}):
                oid = ids.queryId(removeAllProxies(object))
                if oid is None:
                    return ResultSet(IFBTree(), getUtility(ISubscriptions))

                query['object'] = {'any_of': (oid,)}
            else:
                query['object'] = object

        # context
        if not contexts:
            contexts = (getSite(),)

        c = []
        for context in contexts:
            id = ids.queryId(removeAllProxies(context))
            if id is not None:
                c.append(id)

        query['contexts'] = {'any_of': c}

        # visibility
        if visibility is not None:
            query['visibility'] = {'any_of': (visibility,)}

        # apply searh terms
        return ResultSet(self.apply(query), getUtility(ISubscriptions))


@component.adapter(ISubscriptionsCatalog, IObjectAddedEvent)
def handleCatalogAdded(catalog, ev):
    catalog['type'] = ValueIndex('type')
    catalog['principal'] = ValueIndex('principal')
    catalog['object'] = ValueIndex('value', IndexableObject)
    catalog['contexts'] = SetIndex('value', IndexableContexts)


class IndexableObject(object):

    def __init__(self, record, default=None):
        self.value = getUtility(IIntIds).getId(removeAllProxies(record.object))


class IndexableContexts(object):

    def __init__(self, record, default=None):
        values = []
        ids = getUtility(IIntIds)

        context = removeAllProxies(record.object)
        while context is not None:
            values.append(ids.queryId(context))

            context = removeAllProxies(
                getattr(context, '__parent__', None))

        self.value = values


class VisibilityIndex(object):
    component.adapts(ISubscriptionsCatalog)
    interface.implements(ICatalogIndexFactory)

    def __init__(self, catalog):
        self.catalog = catalog

    def __call__(self):
        return ValueIndex('value', IndexableVisibility)


class IndexableVisibility(object):

    def __init__(self, subscription, default=None):
        self.value = default
        principal = getPrincipal(subscription.principal)
        if principal:
            self.value = checkPermissionForPrincipal(
                        principal,
                        'zope.View', subscription.object)


#deprecated
class IndexableSecurityInformation(object):

    def __init__(self, record, default=None): self.value = ()
