import urllib2

from hamcrest import (assert_that, is_)
import time

#from . import BasicSeverOperation

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class GetGroupObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
		self.setValues(kwargs)

		test_args = self.obj_setUp()
		assert test_args, "Invalid operation set up arguments"

		#self.set_time() # self.preRequestTime = time.time()
		assert self.href_url
		# Make a BRAND NEW REQUEST to the dataserver based on
		# self.href_url, which hopefully has some relation to ``url``
		# Read the 'Last Modified' value from the return of that request,
		# and store it in self.lastModifiedCollection
		self.preRequestTime = self.set_collection_modification_time()

		url = self.format.formatURL(test_args['url_id'])
		try:
			request = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(request)
			self.obj_tearDown()

			# Identical to: self.lastModified = parsed_body['LastModified']
			self.set_modification_time(parsed_body)

			assert_that( self.responseCode['get'], is_( request.code ) )


			self.objTest.testBody(	parsed_body, self.postObjData['MimeType'],
									self.objResponse['postExpectedResponse'])

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
													collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)
		except urllib2.HTTPError as error:
			self.obj_tearDown()
			self.set_collection_modification_time()

			assert_that( self.responseCode['get'], is_( error.code ) )


			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
													collectionTime=self.lastModifiedCollection)
