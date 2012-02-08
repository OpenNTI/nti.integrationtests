import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation

class GetGroupObject(BasicSeverOperation):	

	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		
		test_args = self.obj_setUp()
		assert test_args, "Invalid operation set up arguments"
		
		self.set_time()
		url = self.format.formatURL(test_args['url_id'])
		try:
			request = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsed_body = self.format.read(request)
			self.obj_tearDown()
			
			self.set_collection_modification_time()
			self.set_modification_time(parsed_body)
			
			assert	request.code==self.responseCode['get'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], request.code)
			
			self.objTest.testBody(	parsed_body, self.postObjData['MimeType'], 
									self.objResponse['postExpectedResponse'])
			
			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, 
													collectionTime=self.lastModifiedCollection,
													requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.obj_tearDown()
			self.set_collection_modification_time()
			
			assert	error.code==self.responseCode['get'], \
					'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], error.code)
			
			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime,
													collectionTime=self.lastModifiedCollection)
