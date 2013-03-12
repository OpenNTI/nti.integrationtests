#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_message
from nti.integrationtests.integration import container_of_length

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import greater_than_or_equal_to

from nose.plugins.attrib import attr

@attr(priority=3)
class TestBasicRedactions(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicRedactions, self).setUp()
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)

	def test_create_redaction(self):
		st = generate_message()
		created_obj =  self.ds.create_redaction(selectedText=st, replacementContent='redaction',
												redactionExplanation='explanation', container=self.container,
												 adapt=True)

		assert_that(created_obj['selectedText'], is_(st))
		assert_that(created_obj['replacementContent'], is_('redaction'))
		assert_that(created_obj['redactionExplanation'], is_('explanation'))
		
	def test_search_shared(self):
		self.ds.set_credentials(self.owner)	
		
		redaction =  self.ds.create_redaction(selectedText='Zangetsu', replacementContent='Katen Kyokotsu',
											  redactionExplanation='Sogyo no Kotowari', container=self.container,
											  adapt=True)
		self.ds.share_object(redaction, self.target[0], adapt=True)
		time.sleep(2)
		
		self.ds.set_credentials(self.target)
		result = self.ds.search_user_content("Zangetsu")
		assert_that(result, container_of_length(greater_than_or_equal_to(1)))
		
		result = self.ds.search_user_content("Kotowari")
		assert_that(result, container_of_length(greater_than_or_equal_to(1)))
		
		result = self.ds.search_user_content("Kyokotsu")
		assert_that(result, container_of_length(greater_than_or_equal_to(1)))
		
		self.ds.set_credentials(self.target)
		result = self.ds.search_user_content("Engetsu")
		assert_that(result, container_of_length(0))
		
if __name__ == '__main__':
	unittest.main()
