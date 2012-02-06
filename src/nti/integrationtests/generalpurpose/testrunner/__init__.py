import sys
import json
import time
import urllib2

from nti.integrationtests.generalpurpose import USERNAME, PASSWORD, URL
from nti.integrationtests.generalpurpose.utils.generaterequest import ServerRequest
from nti.integrationtests.generalpurpose.utils.url_formatter import NoFormat

def _http_ise_error_logging(f):
	def to_call( *args, **kwargs ):
		try:
			return f( *args, **kwargs )
		except urllib2.HTTPError as http:
			# If the server sent us anything,
			# try to use it
			_, _, tb = sys.exc_info()
			try:
				http.msg += ' URL: ' + http.geturl()
				body = http.read()
				# The last 20 or so lines
				http.msg += ' Body: ' + str( body )[-1600:]
			except (AttributeError, IOError): pass
			http.msg += '\n Args: ' + str(args)
			http.msg += '\n KWArgs: ' + str(kwargs)
			# re-raise the original exception object
			# with the original traceback
			raise http, None, tb
	return to_call

class ServerValues(object):

	def setValues(self, kwargs):
		self.requests = ServerRequest()
		self.format = kwargs.get('format', NoFormat())
		self.objTest = kwargs['bodyTester']
		
		_href = kwargs['href']
		_inputInfo = kwargs['responseTypes']
		_data = kwargs['objRunner']['objects']
		
		self.responseCode = kwargs['responseTypes']
		self.username = USERNAME
		self.password = PASSWORD
		self.testPassword = _inputInfo.get('password', PASSWORD)
		self.postObjData = _data['post_data']
		self.putObjData = _data['put_data']
		self.href_url = URL + _href
		self.testHrefUrl = URL + _inputInfo.get('href', _href)
		self.testObjRef = _inputInfo.get('id', None)
		self.objResponse = kwargs['objRunner']['expected_return']
		
		self.testArgs = None
#		self.lastModifiedCollection = 0
		self.preRequestTime = 0
	
	@_http_ise_error_logging
	def setUp(self):
		if self.testObjRef: 
			self.testArgs = {'url_id':URL + self.testObjRef, 'id':self.testObjRef}
		else:
			url = self.format.formatURL(self.href_url)
			data = self.format.write(self.postObjData)
			request = self.requests.post(url=url, data=data, username=self.username, password=self.password)
			parsedBody = self.format.read(request)
			if parsedBody['href'].find('/Objects/') != -1: self.testArgs = {'url_id':URL + parsedBody['href'], 'id':parsedBody['href']}
			else: self.testArgs = None

		return self.testArgs
	
	def tearDown(self, objref=None):
		try:
			if objref:
				self.requests.delete(url=URL+objref, username=self.username, password=self.password)
			else:
				self.requests.delete(url=self.testArgs['url_id'], username=self.username, password=self.password)
		except urllib2.HTTPError: pass
	
	@classmethod
	def http_ise_error_logging(cls, f):
		_http_ise_error_logging(f)
	
	def setModificationTime(self, parsedBody):
		try:
			self.lastModified = parsedBody['LastModified']
		except KeyError: self.lastModified = None
	
	def setCollectionModificationTime(self):
		try:
			request = self.requests.get(self.href_url, USERNAME, PASSWORD)
			parsedBody = json.loads(request.read())
			self.lastModifiedCollection = parsedBody['Last Modified']
		except urllib2.HTTPError or KeyError: self.lastModifiedCollection = None

	def setTime(self):
		self.preRequestTime = time.time()
