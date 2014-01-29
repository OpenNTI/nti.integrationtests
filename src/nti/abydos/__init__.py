#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import inspect
import numbers
import collections

def toExternalObject(obj):

    def recall(obj):
        if hasattr(obj, 'toExternalObject'):
            result = obj.toExternalObject()
        elif inspect.isfunction(obj):
            result = '%s.%s' % (obj.__module__, obj.__name__)
        elif isinstance(obj, (numbers.Number, six.string_types)):
            result = obj
        elif isinstance(obj, collections.Mapping):
            result = {}
            for key, value in obj.iteritems():
                result[key] = recall(value)
            result = None if not result else result
        elif isinstance(obj, (collections.Set, collections.Sequence)):
            result = [recall(v) for v in obj]
        else:
            result = repr(obj) if obj is not None else None
        return result

    return recall(obj)
