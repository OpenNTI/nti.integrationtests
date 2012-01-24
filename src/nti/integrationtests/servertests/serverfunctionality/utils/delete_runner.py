'''
Created on Jan 12, 2012

@author: ltesti
'''

import urllib2

from servertests.serverfunctionality.utils.request_generator import ServerValues
from servertests.serverfunctionality.utils.response_assert import LastModifiedAssessment

class DeleteObject(ServerValues):
#	@ServerValues.http_ise_error_logging
	def makeRequest(self, kwargs):
		self.setValues(kwargs)
		testArgs = self.setUp()
		url = self.format.formatURL(testArgs['url_id'])
		self.setTime()
		try:
			if not testArgs: assert False, "Attempted a request on a non object"
			request = self.requests.delete(url=url, username=self.username, password=self.testPassword)
			self.setCollectionModificationTime()
			assert request.code==self.responseCode.delete, \
				'this method was expecting a %d response, instead received %d' % (self.responseCode.delete, request.code)
			LastModifiedAssessment.changedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
		except urllib2.HTTPError, error:
			if error.code != 404:
				parsedBody = self.format.read(self.requests.get(url=url, username=self.username, password=self.password))
				self.tearDown()
				self.setCollectionModificationTime()
				self.setModificationTime(parsedBody)
				self.objTest.testBody(parsedBody, self.testObjData['MimeType'], self.objResponse['setupExpectedResponse'])
				LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection,
														requestTime=self.lastModified)
			else: 
				self.setCollectionModificationTime()
				LastModifiedAssessment.unchangedLastModifiedTime(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
			assert error.code==self.responseCode.delete, \
				'this method was expecting a %d response, instead received %d' % (self.responseCode.delete, error.code)