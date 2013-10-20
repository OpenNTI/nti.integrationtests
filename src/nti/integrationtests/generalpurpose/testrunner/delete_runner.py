#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import requests

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class DeleteObject(BasicSeverOperation):

	def makeRequest(self, kwargs):	
			
		self.setValues(kwargs)

		test_args = self.obj_setUp()
		assert test_args, "Invalid operation set up arguments"
		
		self.set_time()
		url = self.format.formatURL(test_args['url_id'])
		try:			
			response = self.requests.delete(url=url, username=self.username, password=self.testPassword)
			self.set_collection_modification_time()
			
			assert 	response.status_code == self.responseCode['delete'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['delete'], response.status_code)
					
			self.check_changed_last_modified_time(	preRequestTime=self.preRequestTime, 
													collectionTime=self.lastModifiedCollection)
			
		except requests.exceptions.HTTPError, error:
			response = getattr(error, 'response', None)
			code = getattr(response, 'status_code', None)

			if code != 404:
				parsed_body = self.format.read(self.requests.get(url=url,
																 username=self.username, 
																 password=self.password))
				self.obj_tearDown()
				
				self.set_collection_modification_time()
				self.set_modification_time(parsed_body)
				self.objTest.testBody(	parsed_body, self.postObjData['MimeType'], 
										self.objResponse['postExpectedResponse'])
				
				self.check_unchanged_last_modified_time(preRequestTime = self.preRequestTime,
														collectionTime = self.lastModifiedCollection,
														requestTime = self.lastModified)
			else: 
				self.set_collection_modification_time()
				self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
														collectionTime=self.lastModifiedCollection)
			
			assert	code == self.responseCode['delete'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['delete'], code)
