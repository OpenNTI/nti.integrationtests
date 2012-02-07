import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation
from nti.integrationtests.generalpurpose.utils.response_assert import LastModifiedAssessment

class GetGroupObject(BasicSeverOperation):	

	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		testArgs = self.obj_setUp()
		self.setTime()
		url = self.format.formatURL(testArgs['url_id'])
		try:
			if not testArgs: assert False, "Attempted a request on a non object"
			request = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsedBody = self.format.read(request)
			self.obj_tearDown()
			self.setCollectionModificationTime()
			self.setModificationTime(parsedBody)
			assert request.code==self.responseCode['get'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], request.code)
			self.objTest.testBody(parsedBody, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.obj_tearDown()
			self.setCollectionModificationTime()
			assert error.code==self.responseCode['get'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], error.code)
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)