#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import requests

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class PutObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
		__traceback_info__ = self._traceback_info_
		self.setValues(kwargs)

		test_args = self.obj_setUp()
		assert test_args, "Invalid operation set up arguments"

		url = self.format.formatURL(test_args['url_id'])
		data = self.format.write(self.putObjData)

		self.set_time()
		try:
			response = self.requests.put(url=url, data=data, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(response)

			self.obj_tearDown()
			self.set_collection_modification_time()
			self.set_modification_time(parsed_body)

			assert	response.status_code == self.responseCode['put'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['put'], response.status_code)

			self.objTest.testBody(parsed_body, self.putObjData['MimeType'], self.objResponse['putExpectedResponse'])

			self.check_changed_last_modified_time(	preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)

		except requests.exceptions.HTTPError, error:
			response = getattr(error, 'response', None)
			code = getattr(response, 'status_code', None)

			self.obj_tearDown()
			self.set_collection_modification_time()

			assert 	code == self.responseCode['put'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['put'], code)

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
