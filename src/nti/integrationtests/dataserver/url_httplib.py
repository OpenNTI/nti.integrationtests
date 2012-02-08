import os
import sys
import json
import pprint
import httplib
import urllib2
import mimetools
import mimetypes
from io import BytesIO
from cStringIO import StringIO

from webob import Response

class URLHttpLib(object):

	def __init__(self, debug=False):
		self.debug = debug

	# -----------------------------------

	@classmethod
	def _get_encoding(cls, obj):
		data = None

		if isinstance(obj, httplib.HTTPMessage):
			data = obj.headers.dict.get('content-type', None)
		elif isinstance(obj, dict):
			data = obj.get('content-type', None)

		data = str(data) if data else 'UTF-8'
		if data.find('charset=') != -1:
			data = data[data.find('charset=') + 8:]
		return data
	
	@classmethod
	def _create_response(cls, code=None, rp=None):
		status = rp.code if rp else code
		body = rp.read() if rp else u''
		headers = rp.headers.dict if rp else {}
		headerlist = [(k,v) for k,v in headers.items()]
		charset = cls._get_encoding(headers)
		return Response(body=body, status=status, headerlist=headerlist, charset=charset)

	# -----------------------------------
	
	def _create_request(self, credentials, url, data=None, headers={}):
		request = urllib2.Request(url=url, data=data, headers=headers)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, credentials[0], credentials[1])
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		return request

	def _do_request(self, request, *args, **kwargs):
		try:
			rp = urllib2.urlopen(request)
			return self._create_response(rp=rp)
		except urllib2.HTTPError as http:
			
			# handle 404s differently
			if http.code == 404:
				return URLHttpLib._create_response(code=404)
			
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

	def _do_debug(self, url, rp, credentials):
		if self.debug:
			raw_content = rp.body
			try:
				dt = self.deserialize(rp) if raw_content else {}
			except Exception, e:
				dt = {'Exception': e}
			d = {'data':dt, 'url':url, 'auth':credentials, 'raw': raw_content}
			pprint.pprint(d)

	# -----------------------------------
	
	def deserialize(self, rp):
		return json.loads(rp.body, encoding=rp.charset)

	def _prune(self, d):
		result = {}
		result.update(d)
		result.pop('self')
		return result
	
	def do_get(self, url, credentials, *args, **kwargs):
		call_args = self._prune(locals())
		request = self._create_request(credentials, url)
		rp = self._do_request(request, **call_args)
		self._do_debug(url, rp, credentials)
		return rp

	def do_post(self, url, credentials, data, *args, **kwargs):
		call_args = self._prune(locals())
		request = self._create_request(credentials, url, data)
		rp = self._do_request(request, **call_args)
		self._do_debug(url, rp, credentials)
		return rp

	def do_put(self, url, credentials, data, *args, **kwargs):
		call_args = self._prune(locals())
		request = self._create_request(credentials, url, data)
		request.get_method = lambda: 'PUT'
		rp = self._do_request(request, **call_args)
		self._do_debug(url, rp, credentials)
		return rp

	def do_delete(self, url, credentials, *args, **kwargs):
		call_args = self._prune(locals())
		request = self._create_request(credentials, url)
		request.get_method = lambda: 'DELETE'
		rp = self._do_request(request, **call_args)
		self._do_debug(url, rp, credentials)
		return rp
	
	def do_upload_resource(self, url, credentials, source_file, content_type=None, headers={}, is_put=False):
		call_args = self._prune(locals())
		
		content_type = content_type if content_type else self._get_mime_type(source_file)
		request = self._create_request(credentials, url, headers={'Content-Type': content_type})
		if is_put: request.get_method =  lambda: 'PUT'	
		request.add_unredirected_header('Content-Type', content_type)
		for k, v in headers.items():
			request.add_unredirected_header(k, v)
		
		# read data								
		buf = BytesIO()
		with open(source_file, "rb") as fd:
			buf.write(fd.read())	
		data = buf.getvalue()
		
		# add and execure request
		request.add_data(data)
		rp = self._do_request(request, **call_args)
		self._do_debug(url, rp, credentials)
		return rp
	
	def _get_mime_type(self, source):
		filename = os.path.basename(source)
		return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
	
	# -----------------------------------
	
	def do_upload_resources(self, url, credentials, files, default_content_type=None, headers={} ):
		""" 
		Implements multipart resource upload.
		This is not currently supported by the dataserver
		"""
		request = self._create_request(credentials, url)
		boundary, data = self.multipart_encode(files, default_content_type)
		content_type = 'multipart/form-data; boundary=%s' % boundary
		request.add_unredirected_header('Content-Type', content_type)
		for k, v in headers.items():
			request.add_unredirected_header(k, v)
			
		request.add_data(data)
		rp = self._do_request(request, **locals())
		self._do_debug(url, rp, credentials)
		return rp
		
	def multipart_encode(self, files, default_content_type=None, boundary=None, buf=None):

		buf = buf or StringIO()
		boundary = boundary or mimetools.choose_boundary()
		
		for n, source in enumerate(files):
			filename = os.path.basename(source)
			content_type = default_content_type if default_content_type else self._get_mime_type(filename)
		
			key = 'updloaded_%s' % n
			buf.write('--%s\r\n' % boundary)
			buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
			buf.write('Content-Type: %s\r\n' % content_type)
			with open(source, "rb") as fd:
				buf.write('\r\n' + fd.read() + '\r\n')
			
		buf.write('--' + boundary + '--\r\n\r\n')
		buf = buf.getvalue()
		return boundary, buf
	

