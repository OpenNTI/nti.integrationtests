#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import requests

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

from hamcrest import assert_that, is_

class GetObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
		self.setValues(kwargs)

		test_args = self.obj_setUp()
		__traceback_info__ = self._traceback_info_, kwargs, test_args
		assert test_args, "Invalid operation set up arguments"

		self.set_time()
		self.preRequestTime = self.set_collection_modification_time()
		url = self.format.formatURL(test_args['url_id'])
		try:
			response = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(response)

			ifModifiedSinceYes = self.requests.ifModifiedSinceYes(url=test_args['url_id'],
																  username=self.username,
																  password=self.testPassword)

			ifModifiedSinceNo = self.requests.ifModifiedSinceNo(url=test_args['url_id'],
																username=self.username,
																password=self.testPassword)

			self.obj_tearDown()

			self.set_modification_time(parsed_body)
			__traceback_info__ = self._traceback_info_, kwargs, test_args, response, ifModifiedSinceYes, ifModifiedSinceNo, parsed_body
			assert_that(response.status_code, is_(self.responseCode['get']),
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], response.status_code))

			assert_that( ifModifiedSinceYes, is_( self.responseCode['if_modified_since_yes'] ),
					'this method was expecting a %d response, instead received %d' % (self.responseCode['if_modified_since_yes'], ifModifiedSinceYes) )

			assert_that( ifModifiedSinceNo, is_( self.responseCode['if_modified_since_no'] ),
					'this method was expecting a %d response, instead received %d' % (self.responseCode['if_modified_since_no'], ifModifiedSinceNo) )

			self.objTest.testBody(parsed_body, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
													collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)

		except requests.exceptions.HTTPError, error:
			response = getattr(error, 'response', None)
			code = getattr(response, 'status_code', None)

			self.obj_tearDown()
			self.set_collection_modification_time()

			assert_that( error.code, is_( self.responseCode['get'] ),
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], code))

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
