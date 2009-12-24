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
""" zojax.subscription interfaces

$Id$
"""
from zope import interface
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import IObjectEvent

_ = MessageFactory('zojax.subscription')


class SubscriptionException(Exception):
    """ general subscription exception """


class UnknownPrincipalException(SubscriptionException):
    """ principal is unknown """


class ISubscription(interface.Interface):
    """ principal subscription """

    id = interface.Attribute('Id')
    oid = interface.Attribute('Object Id')
    principal = interface.Attribute('Principal')

    # static info
    type = interface.Attribute('Record type')
    object = interface.Attribute('Content Object')
    description = interface.Attribute('ISubscriptionDescription Object')


class ISubscriptionDescription(interface.Interface):
    """ subscription description object """

    title = interface.Attribute('Title')
    description = interface.Attribute('Description')


class ISubscriptions(interface.Interface):
    """ configlet subscriptions """

    catalog = interface.Attribute('Catalog')
    subscriptions = interface.Attribute('Subscriptions')

    def add(object, record):
        """ add activity record """

    def remove(rid):
        """ remove activity record """

    def removeObject(object):
        """ remove records for object """

    def removeSubscription(object, principal, type):
        """ remove subscription """

    def unsubscribePrincipal(principal, id):
        """ unsubscribe principal """

    def principalSubscriptions(principal):
        """ return principal subscriptions """

    def objectSubscriptions(object):
        """ return object subscriptions """

    def updateObjectSubscriptions(object):
        """ reindex subscriptions for object """

    def search(**kw):
        """ search subscriptions """

    def getObject(id):
        """ return subscription by id """


class ISubscriptionEvent(IObjectEvent):
    """ subscription event """

    subscription = interface.Attribute("Subscription")


class ISubscriptionAddedEvent(ISubscriptionEvent):
    """ subscription added event """


class ISubscriptionRemovedEvent(ISubscriptionEvent):
    """ subscription removed event """


class ISubscriptionsCatalog(interface.Interface):
    """ subscriptions catalog """
