import sys
import json
import time
import urllib2
from urlparse import urljoin

from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to, has_entry

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
			except (AttributeError, IOError):
				pass

			http.msg += '\n Args: ' + str(args)
			http.msg += '\n KWArgs: ' + str(kwargs)

			# re-raise the original exception object
			# with the original traceback
			raise http, None, tb

	return to_call

class BasicSeverOperation(object):

	requests = None
	objTest = None
	format = None
	endpoint = None
	username = None
	password = None
	responseCode = None
	testPassword = None
	href_url = None
	putObjData = None
	postObjData = None
	testObjRef = None
	objResponse = None
	testHrefUrl = None
	testArgs = None
	lastModified = None
	lastModifiedCollection = None
	preRequestTime = None

	def setValues(self, kwargs):

		self.requests = ServerRequest()
		self.objTest = kwargs['bodyTester']
		self.format  = kwargs.get('format', NoFormat())

		_href = kwargs['href']
		_input_info = kwargs['responseTypes']
		_data = kwargs['objRunner']['objects']

		self.endpoint = kwargs['endpoint']
		self.username = kwargs['username']
		self.password = kwargs['password']
		self.responseCode = kwargs['responseTypes']
		self.testPassword = _input_info.get('password', self.password)

		self.href_url = urljoin(self.endpoint, _href)
		self.putObjData = _data['put_data']
		self.postObjData = _data['post_data']

		self.testObjRef = _input_info.get('id', None)
		self.objResponse = kwargs['objRunner']['expected_return']
		self.testHrefUrl = urljoin(self.endpoint, _input_info.get('href', _href))

		self.testArgs = None
		self.preRequestTime = 0


	@_http_ise_error_logging
	def obj_setUp(self):
		if self.testObjRef:
			url = urljoin(self.endpoint, self.testObjRef)
			self.testArgs = {'url_id':url, 'id' : self.testObjRef}
		else:
			url = self.format.formatURL(self.href_url)
			data = self.format.write(self.postObjData)
			request = self.requests.post(url=url, data=data, username=self.username, password=self.password)
			parsed_body = self.format.read(request)

			if parsed_body['href'].find('/Objects/') != -1:
				url = urljoin(self.endpoint, parsed_body['href'])
				self.testArgs = {'url_id':url, 'id' : parsed_body['href']}
			else:
				self.testArgs = None
		return self.testArgs

	def obj_tearDown(self, objref=None):
		try:
			url = urljoin(self.endpoint, objref) if objref else self.testArgs['url_id']
			self.requests.delete(url=url, username=self.username, password=self.password)
		except urllib2.HTTPError:
			pass

	@classmethod
	def http_ise_error_logging(cls, f):
		_http_ise_error_logging(f)

	def set_modification_time(self, parsed_body):
		try:
			self.lastModified = parsed_body['LastModified']
		except KeyError:
			self.lastModified = None
	setModificationTime = set_modification_time

	def set_collection_modification_time(self):
		try:
			request = self.requests.get(self.href_url, self.username, self.password)
			parsed_body = json.loads(request.read())
			self.lastModifiedCollection = parsed_body['Last Modified']
		except urllib2.HTTPError or KeyError:
			self.lastModifiedCollection = None
	setCollectionModificationTime = set_collection_modification_time

	def set_time(self):
		self.preRequestTime = time.time()
	setTime = set_time

	def check_changed_last_modified_time(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		lastModifiedTime = kwargs.get('requestTime', None)
		preRequestTime = kwargs['preRequestTime']
		if lastModifiedTimeCollection:
			assert_that( kwargs, has_entry( 'collectionTime', greater_than_or_equal_to( preRequestTime ) ) )

		if lastModifiedTime:
			assert_that( kwargs, has_entry( 'requestTime', greater_than_or_equal_to( preRequestTime ) ) )



	changedLastModifiedTime = check_changed_last_modified_time

	def check_unchanged_last_modified_time(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		preRequestTime = kwargs['preRequestTime']
		lastModifiedTime = kwargs.get('requestTime', None)
		if lastModifiedTimeCollection:
			assert_that( kwargs, has_entry( 'collectionTime', less_than_or_equal_to( preRequestTime ) ) )

		if lastModifiedTime:
			assert_that( kwargs, has_entry( 'requestTime', less_than_or_equal_to( preRequestTime ) ) )


	unchangedLastModifiedTime = check_unchanged_last_modified_time

