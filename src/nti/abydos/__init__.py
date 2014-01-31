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

import ZODB

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

def alias(prop_name, doc=None):
    if doc is None:
        doc = 'Alias for :attr:`' + prop_name + '`'
    return property(lambda self: getattr(self, prop_name),
                    lambda self, nv: setattr(self, prop_name, nv),
                    doc=doc)

def make_repr():
    def __repr__(self):
        try:
            return "%s().__dict__.update( %s )" % (self.__class__.__name__, self.__dict__)
        except ZODB.POSException.ConnectionStateError:
            return '%s(Ghost)' % self.__class__.__name__
        except (ValueError, LookupError) as e:
            return '%s(%s)' % (self.__class__.__name__, e)
    return __repr__
