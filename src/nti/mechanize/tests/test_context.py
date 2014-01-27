#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property

import unittest

from nti.mechanize.context import Context
from nti.mechanize.context import DelegateContext

class TestContext(unittest.TestCase):
	
	def test_context(self):
		c = Context()
		c.test = 'test'
		assert_that(c, has_property('test', 'test'))
		d = DelegateContext(c)
		assert_that(d, has_property('test', 'test'))
		d.test1 = 'test1'
		assert_that(d, has_property('test1', 'test1'))
		try:
			d.test = 'xxx'
			self.fail()
		except AttributeError:
			pass

		c['foo'] = 1
		assert_that(c, has_property('foo', is_(1)))
		assert_that(c, has_entry('foo', is_(1)))
		c.foo = 2
		assert_that(c, has_property('foo', is_(2)))

		assert_that(d, has_property('foo', is_(2)))
		assert_that(d, has_entry('foo', is_(2)))
