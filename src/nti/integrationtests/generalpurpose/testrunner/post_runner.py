import urllib2

from nti.integrationtests.generalpurpose.testrunner import BasicSeverOperation
import sys

class PostObject(BasicSeverOperation):

	def makeRequest(self, kwargs):
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
		except urllib2.HTTPError, error:
			self.set_collection_modification_time()

			if error.code != self.responseCode['post']:
				# If the server sent us anything,
				# try to use it
				_, _, tb = sys.exc_info()
				try:
					error.msg += ' URL: ' + error.geturl()
					body = error.read()
					# The last 20 or so lines
					error.msg += ' Body: ' + str( body )[-1600:]
				except (AttributeError, IOError):
					pass

				error.msg += '\n KWArgs: ' + str(kwargs)
				error.msg += '\n This method was expecting a %s response, instead received %s' % (self.responseCode['post'], error.code)
				# re-raise the original exception object
				# with the original traceback
				raise error, None, tb


			self.check_unchanged_last_modified_time(preRequestTime=self.preRequestTime, collectionTime=self.lastModifiedCollection)
