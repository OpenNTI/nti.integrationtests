import requests

from collections import deque

from nti.integrationtests.socketio import SocketIOSocket
from nti.integrationtests.socketio import SocketIOException

import logging
logger = logging.getLogger(__name__)

class XHRPollingSocketException(SocketIOException):
	pass

class XHRPollingSocket(SocketIOSocket):
		
	_WS_CONNECT					  = b'1::'
	_LIGHTWEIGHT_FRAME_DELIM      = b'\xff\xfd'     # u'\ufffd', the opening byte of a lightweight framing
	_LIGHTWEIGHT_FRAME_UTF8_DELIM = b'\xef\xbf\xbd' # utf-8 encoding of u'\ufffd'

	def __init__(self):
		super(SocketIOSocket, self).__init__()
		self.queue = deque([])

	def connect(self, url, auth, *args, **kwargs):
		self.connected = True
		self.url = url
		self.auth = auth
		
	def send(self, payload):
		if isinstance( payload, unicode ):
			payload = payload.encode( 'utf-8' )
		r = requests.post(self.url, auth=self.auth, data=payload)
		if r.status_code != 200:
			raise XHRPollingSocketException("Could not post message '%s' to '%s'" % (payload, self.url))
		
	def recv(self):
		if self.queue:
			result = self.queue.popleft() 
		else:
			r = requests.get(self.url, auth=self.auth)
			if r.status_code != 200:
				raise XHRPollingSocketException("Could not get messages from '%s'" % self.url)
			for msg in self.decode_multi(r.text):
				self.queue.append(msg)
			result = self.queue.popleft() if self.queue else None
		return result

	def close(self):
		self.connected = False
	
	def decode_multi(self, data ):
		"""
		:return: A sequence of Message objects
		"""
		DELIM1 = self._LIGHTWEIGHT_FRAME_DELIM
		DELIM2 = self._LIGHTWEIGHT_FRAME_UTF8_DELIM
	
		# If they give us a unicode object (weird!)
		# encode as bytes in utf-8 format
		if isinstance( data, unicode ):
			data = data.encode( 'utf-8' )
		assert isinstance( data, str ), "Must be a bytes object, not unicode"
	
		if not data.startswith( DELIM1 ) and not data.startswith( DELIM2 ):
			# Assume one
			return ( data, )
	
		d = DELIM1
		dl = 2
		if data.startswith( DELIM2 ):
			d = DELIM2
			dl = 3
	
		messages = []
		start = 0
		while start + dl < len(data):
			start_search = start + dl
			end = data.find( d, start_search )
			len_str = int( data[start_search:end] )
			if len_str <= 0: raise ValueError( 'Bad length' )
			end_data = end + dl + len_str
			sub_data = data[end+dl:end_data]
			if not sub_data:
				raise XHRPollingSocketException( "Data from %s to %s was not len %s (got %s)" % (start_search, end_data, len_str, sub_data ) )
			if not len(sub_data) == len_str:
				raise XHRPollingSocketException( "Data from %s to %s was not len %s (got %s)" % (start_search, end_data, len_str, sub_data ) )
			messages.append( sub_data  )
	
			start = end_data
	
		return messages

	@classmethod
	def connect_to_ds(cls, host, port, username, password, is_secure=False, resource=None, **kwargs):
		resource = resource or '/socket.io/1/'
		resource = resource + '/' if resource[-1] != '/' else resource
		protocol = 'https' if is_secure else 'http'
		hostport = "%s:%s" % (host, port)
		
		auth = (username, password)
		url = '%s://%s' % (protocol, hostport)
		
		urlf = url + resource
		r = requests.post(urlf, auth=auth)
		if r.status_code == 200:
			msg = r.text
			sessiond_id = msg.split(':')[0]
			resource = '%s%s/%s' % (resource, 'xhr-polling', sessiond_id)
			urlf = url + resource
			headers = {'Origin': hostport, 'Host':hostport}
			r = requests.post(urlf, auth=auth, headers=headers)
			
			if r.status_code != 200 or r.text != cls._WS_CONNECT:
				raise XHRPollingSocketException("Could not set connection to %s" % urlf)
			
			result = XHRPollingSocket()
			result.connect(urlf, auth)
		else:
			raise XHRPollingSocketException("Invalid status code while posting to %s" % urlf)
	

	
	