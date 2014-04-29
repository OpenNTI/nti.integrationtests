#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import sys
import requests

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class PostObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
		__traceback_info__ = self._traceback_info_
		self.setValues(kwargs)

		url = self.format.formatURL(self.testHrefUrl)
		data = self.format.write(self.postObjData)

		self.set_time()
		try:
			request = self.requests.post(url=url, data=data, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(request)

			self.obj_tearDown(parsed_body['href'])
			self.set_collection_modification_time()
			self.set_modification_time(parsed_body)

			assert	request.code==self.responseCode['post'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['post'], request.code)

			self.objTest.testBody(parsed_body, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])

			self.check_changed_last_modified_time(	preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)
		except requests.exceptions.HTTPError as error:
			response = getattr(error, 'response', None)
			code = getattr(response, 'status_code', None)

			self.set_collection_modification_time()

			if code != self.responseCode['post']:
				# If the server sent us anything,
				# try to use it
				_, _, tb = sys.exc_info()
				message = error.message
				message += '\n KWArgs: ' + str(kwargs)
				message += '\n This method was expecting a %s response, instead received %s' % (self.responseCode['post'], code)

				# re-raise the original exception object
				# with the original traceback
				raise error.__class__(message, response=response), None, tb

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
