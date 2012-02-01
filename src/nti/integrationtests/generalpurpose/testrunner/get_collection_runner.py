import urllib2

from nti.integrationtests.generalpurpose.testrunner import ServerValues
from nti.integrationtests.generalpurpose.utils.response_assert import LastModifiedAssessment

class GetGroupObject(ServerValues):	
#	@ServerValues.http_ise_error_logging
	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		testArgs = self.setUp()
		self.setTime()
		url = self.format.formatURL(testArgs['url_id'])
		try:
			if not testArgs: assert False, "Attempted a request on a non object"
			request = self.requests.get(url=url, username=self.username, password=self.testPassword)
			parsedBody = self.format.read(request)
			self.tearDown()
			self.setCollectionModificationTime()
			self.setModificationTime(parsedBody)
			assert request.code==self.responseCode['get'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], request.code)
			self.objTest.testBody(parsedBody, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.tearDown()
			self.setCollectionModificationTime()
			assert error.code==self.responseCode['get'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['get'], error.code)
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)