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
from zope.security.management import queryInteraction
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from interfaces import UnknownPrincipalException


def getPrincipal():
    """ get current interaction principal """
    interaction = queryInteraction()

    if interaction is not None:
        for participation in interaction.participations:
            if participation.principal is not None:
                return participation.principal

    raise UnknownPrincipalException()


def getPrincipals(ids):
    auth = getUtility(IAuthentication)

    for pid in ids:
        try:
            principal = auth.getPrincipal(pid)
        except PrincipalLookupError:
            continue

        yield principal
