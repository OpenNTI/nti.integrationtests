#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest

from nti.integrationtests import DataServerTestCase
from hamcrest import (has_key, is_not, assert_that, greater_than, has_length, none, has_property)

from nose.plugins.attrib import attr

@attr(level=3)
class TestBasicDevice(DataServerTestCase):
	
	name = 'deadbeef'
	owner = ('test.user.1', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicDevice, self).setUp()
		self.ds.set_credentials(self.owner)

	def test_devices(self):
		device = self.ds.register_device(id_=self.name)
		assert_that(device, is_not(none()))
		assert_that(device, has_property('id', self.name))
		
		devices = self.ds.get_devices()
		assert_that(devices, has_length(greater_than(0)))
		assert_that(devices, has_key(self.name))

		self.ds.delete_object(device)

if __name__ == '__main__':
	unittest.main()
