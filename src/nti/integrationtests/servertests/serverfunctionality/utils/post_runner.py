'''
Created on Jan 12, 2012

@author: ltesti
'''

import urllib2

from servertests.serverfunctionality.utils.request_generator import ServerValues
from servertests.serverfunctionality.utils.response_assert import LastModifiedAssessment

class PostObject(ServerValues):
#	@ServerValues.http_ise_error_logging
	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		url = self.format.formatURL(self.testHrefUrl)
		data = self.format.write(self.testObjData)
		self.setTime()
		try:
			request = self.requests.post(url=url, data=data, username=self.username, password=self.testPassword)
			parsedBody = self.format.read(request)
			self.tearDown(parsedBody['href'])
			self.setCollectionModificationTime()
			self.setModificationTime(parsedBody)
			assert request.code==self.responseCode.post, \
				'this method was expecting a %d response, instead received %d' % (self.responseCode.post, request.code)
			self.objTest.testBody(parsedBody, self.testObjData['MimeType'], self.objResponse['testExpectedResponse'])
			LastModifiedAssessment.changedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
		except urllib2.HTTPError, error:
			self.setCollectionModificationTime()
			assert error.code == self.responseCode.post, \
				'this method was expecting a %s response, instead received %s' % (self.responseCode.post, error.code)
			LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)