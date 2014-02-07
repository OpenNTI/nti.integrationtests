#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import time
import uuid
import stripe
import unittest

from nti.integrationtests import DataServerTestCase

from nose.plugins.attrib import attr
from hamcrest import (assert_that, is_, is_not, none)

@attr(level=4)
class TestStore(DataServerTestCase):

	user_one = ('test.user.1@nextthought.com', 'temp001')

	@classmethod
	def setUpClass(cls):
		super(TestStore, cls).setUpClass()
		cls.api_key = stripe.api_key
		stripe.api_key = u'sk_test_3K9VJFyfj0oGIMi7Aeg3HNBp'

	@classmethod
	def tearDownClass(cls):
		super(TestStore, cls).tearDownClass()
		stripe.api_key = cls.api_key

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
		token = self.ds.create_stripe_token(params, timeout=45)
		return token

	def _create_coupon(self, percent_off=None, amount_off=None, duration="once"):
		code = str(uuid.uuid4()).split('-')[0]
		c = stripe.Coupon.create(percent_off=percent_off, amount_off=amount_off, duration=duration, id=code)
		return c

	def _loop_test(self, purchase_id):
		success = False
		for _ in xrange(30):
			time.sleep(1)
			purchase = self.ds.get_purchase_attempt(purchase_id)
			assert_that(purchase, is_not(none()))
			if purchase['State'] == 'Success':
				success = True
				break
		assert_that(success, is_(True))

	def test_purchase(self):
		token = self._create_stripe_token()
		purchase = {
			'purchasableID':'tag:nextthought.com,2011-10:NextThought-purchasable-HelpCenter',
			'amount': 100,
			'token': token}

		purchase = self.ds.post_stripe_payment(purchase)
		assert_that(purchase, is_not(none()))

		purchase_id = purchase.get('ID')
		assert_that(purchase_id, is_not(none()))
		self._loop_test(purchase_id)

	def test_purchase_coupon(self):
		coupon = self._create_coupon(percent_off=50)
		token = self._create_stripe_token()
		purchase = {
			'purchasableID':'tag:nextthought.com,2011-10:NextThought-purchasable-HelpCenter',
			'amount': 50,
			'token': token,
			'coupon':coupon.id}

		purchase = self.ds.post_stripe_payment(purchase)
		assert_that(purchase, is_not(none()))

		purchase_id = purchase.get('ID')
		assert_that(purchase_id, is_not(none()))
		try:
			self._loop_test(purchase_id)
		finally:
			coupon.delete()

if __name__ == '__main__':
	unittest.main()
