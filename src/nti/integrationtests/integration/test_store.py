#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import time
import unittest

from nti.integrationtests import DataServerTestCase

from hamcrest import (assert_that, is_not, none)

from nose.plugins.attrib import attr

@attr(level=4)
class TestStore(DataServerTestCase):

	user_one = ('test.user.1@nextthought.com', 'temp001')

	def setUp(self):
		super(TestStore, self).setUp()
		self.ds.set_credentials(self.user_one)

	def _create_stripe_token(self):
		params = dict(cc="5105105105105100",
					  exp_month="11",
					  exp_year="30",
					  cvc="542",
					  address="3001 Oak Tree #D16",
					  city="Norman",
					  zip="73072",
					  state="OK",
					  country="USA",
					  provider='NTI-TEST')
		token = self.ds.create_stripe_token(params)
		return token

	def test_purchase(self):
		token = self._create_stripe_token()
		purchase = {
			'purchasableID':'tag:nextthought.com,2011-10:NextThought-HTML-NextThoughtHelpCenter.nextthought_help_center',
			'amount': 300,
			'token': token}

		purchase = self.ds.post_stripe_payment(purchase)
		assert_that(purchase, is_not(none()))

		purchase_id = purchase.get('ID')
		assert_that(purchase_id, is_not(none()))

		for _ in xrange(10):
			time.sleep(1)
			purchase = self.ds.get_purchase_attempt(purchase_id)
			assert_that(purchase, is_not(none()))
			if purchase['State'] == 'Success':
				break

if __name__ == '__main__':
	unittest.main()
