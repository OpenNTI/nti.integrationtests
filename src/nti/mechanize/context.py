#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import numbers

from . import boolean_states
from . import toExternalObject

class DataMixin(object):

	def __contains__(self, key):
		return key in self.__dict__

	def __getitem__(self, key):
		return self.__getattr__.get(key)

	def __setitem__(self, key, val):
		self.__setattr__(key, val)

	def __delitem__(self, key):
		del self.__dict__[key]

	def items(self):
		return self.__dict__.items()

	def keys(self):
		return self.__dict__.keys()

	def __str__(self):
		return "%s(%s)" % (self.__class__.__name__, self.__dict__)
	__repr__ = __str__

	def toExternalObject(self):
		external = {}
		for k, v in self.__dict__.items():
			if not k.startswith("_"):
				external[k] = toExternalObject(v)
		return external

class TimerResultMixin(DataMixin):

	def __init__(self, data=None):
		super(TimerResultMixin, self).__init__()
		self.__dict__.update(data or {})

	def __setattr__(self, name, value):
		assert isinstance(value, numbers.Number)
		super(TimerResultMixin, self).__setattr__(name, value)

	@property
	def timers(self):
		return dict(self.__dict__)

class Context(DataMixin):

	def _as(self, trx, key, default=None):
		result = getattr(self, key, default)
		if result is not None:
			result = trx(result)
		return result

	def as_int(self, key, default=None):
		return self._as(int, key, default)

	def as_float(self, key, default=None):
		return self._as(float, key, default)

	def as_bool(self, key, default=None):
		result = self._as(str, key, default)
		if result is not None:
			result = boolean_states[result.lower()]
		return result

	def as_str(self, key, default=None):
		return self._as(str, key, default)

class DelegateContext(Context):

	def __init__(self, context):
		super(DelegateContext, self).__init__()
		assert isinstance(context, Context)
		self.__dict__['_delegated'] = context

	def __contains__(self, key):
		return key in self.__dict__ or key in self._delegated

	def keys(self):
		result = list(self.__dict__.keys()) + list(self._delegated.keys())
		return result

	def items(self):
		result = list(self.__dict__.items()) + list(self._delegated.items())
		return result

	def __getattr__(self, name):
		if name in self._delegated:
			return self._delegated[name]
		return self.__dict__[name]

	def __setattr__(self, name, value):
		if name not in self._delegated:
			self.__dict__[name] = value
		else:
			raise AttributeError('Cannot set a delegated attribute')

	def toExternalObject(self):
		external = self._delegated.toExternalObject()
		for k, v in self.__dict__.items():
			if not k.startswith("_"):
				external[k] = toExternalObject(v)
		return external
