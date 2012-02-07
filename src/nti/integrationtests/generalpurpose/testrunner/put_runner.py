import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation
from nti.integrationtests.generalpurpose.utils.response_assert import LastModifiedAssessment

class PutObject(BasicSeverOperation):	
	
	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		testArgs = self.obj_setUp()
		url = self.format.formatURL(testArgs['url_id'])
		data = self.format.write(self.putObjData)
		self.setTime()
		try:
			if not testArgs: assert False, "Attempted a request on a non object"
			request = self.requests.put(url=url, data=data, username=self.username, password=self.testPassword)
			parsedBody = self.format.read(request)
			self.obj_tearDown()
			self.setCollectionModificationTime()
			self.setModificationTime(parsedBody)
			assert request.code==self.responseCode['put'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['put'], request.code)
			self.objTest.testBody(parsedBody, self.putObjData['MimeType'], self.objResponse['putExpectedResponse'])
			LastModifiedAssessment.changedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.obj_tearDown()
			self.setCollectionModificationTime()
			assert error.code==self.responseCode['put'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['put'], error.code)
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)