import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation
from nti.integrationtests.generalpurpose.utils.response_assert import LastModifiedAssessment

class PostObject(BasicSeverOperation):
	
	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		url = self.format.formatURL(self.testHrefUrl)
		data = self.format.write(self.postObjData)
		self.setTime()
		try:
			request = self.requests.post(url=url, data=data, username=self.username, password=self.testPassword)
			parsedBody = self.format.read(request)
			self.obj_tearDown(parsedBody['href'])
			self.setCollectionModificationTime()
			self.setModificationTime(parsedBody)
			assert request.code==self.responseCode['post'], \
				'this method was expecting a %d response, instead received %d' % (self.responseCode['post'], request.code)
			self.objTest.testBody(parsedBody, self.postObjData['MimeType'], self.objResponse['postExpectedResponse'])
			LastModifiedAssessment.changedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.setCollectionModificationTime()
			assert error.code == self.responseCode['post'], \
				'this method was expecting a %s response, instead received %s' % (self.responseCode['post'], error.code)
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)