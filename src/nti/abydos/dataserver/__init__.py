# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import collections

from .. import toExternalObject

def to_collection(items=None, factory=list):
    result = None
    if not items:
        result = factory()
    elif isinstance(items, factory):
        result = items
    elif isinstance(items, six.string_types) or \
         not isinstance(items, collections.Iterable):
        result = factory([items])
    else:
        result = factory(items)
    return result

def to_list(items=None):
    return to_collection(items, list)

def to_set(items=None):
    return to_collection(items, set)
