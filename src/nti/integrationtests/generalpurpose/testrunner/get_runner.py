import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class GetObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
		__traceback_info__ = self._traceback_info_
		self.setValues(kwargs)

		test_args = self.obj_setUp()
		assert test_args, "Invalid operation set up arguments"

		self.set_time()
		self.preRequestTime = self.set_collection_modification_time()
		url = self.format.formatURL(test_args['url_id'])
		try:
			request = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(request)

			ifModifiedSinceYes = self.requests.ifModifiedSinceYes(url=test_args['url_id'],
																  username=self.username,
																  password=self.testPassword)

			ifModifiedSinceNo = self.requests.ifModifiedSinceNo(url=test_args['url_id'],
																username=self.username,
																password=self.testPassword)

			self.obj_tearDown()

			self.set_modification_time(parsed_body)

			assert 	request.code == self.responseCode['get'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], request.code)

			assert	ifModifiedSinceYes == self.responseCode['if_modified_since_yes'], \
					'this method was expecting a %d response, instead received %d' % (ifModifiedSinceYes, self.responseCode['if_modified_since_yes'])

			assert	ifModifiedSinceNo == self.responseCode['if_modified_since_no'], \
					'this method was expecting a %d response, instead received %d' % (ifModifiedSinceNo, self.responseCode['if_modified_since_no'])

			self.objTest.testBody(parsed_body, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
													collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)

		except urllib2.HTTPError as error:
			self.obj_tearDown()
			self.set_collection_modification_time()

			assert 	error.code==self.responseCode['get'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], error.code)

			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
