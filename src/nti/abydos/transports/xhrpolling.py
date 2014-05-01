#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import requests

from collections import deque

from . import SocketIOSocket
from . import SocketIOException

class XHRPollingSocketException(SocketIOException):
	pass

class XHRPollingSocket(SocketIOSocket):
		
	_WS_NOOP					  = b'8::'
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
		headers = {'content-type':'text/plain'}
		r = requests.post(self.url, auth=self.auth, data=payload, headers=headers)
		if r.status_code != 200:
			raise XHRPollingSocketException(
						"Could not post message '%s' to '%s'" % (payload, self.url))
		
	def recv(self):
		if self.queue:
			result = self.queue.popleft() 
		else:
			r = requests.get(self.url, auth=self.auth)
			if r.status_code != 200:
				raise XHRPollingSocketException(
							"Could not get messages from '%s'" % self.url)
			for msg in self.decode_multi(r.text):
				self.queue.append(msg)
			result = self.queue.popleft() if self.queue else None
		return result

	def close(self):
		self.connected = False
	
	def heartbeat(self):
		pass
	
	def isHeartBeat(self, msg):
		return str(msg).startswith(self._WS_NOOP)
	
	isNOOP = isHeartBeat
	
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
			if len_str <= 0: 
				raise XHRPollingSocketException( 'Bad length' )
			end_data = end + dl + len_str
			sub_data = data[end+dl:end_data]
			if not sub_data:
				raise XHRPollingSocketException(
							"Data from %s to %s was not len %s (got %s)" %
							(start_search, end_data, len_str, sub_data))
			if not len(sub_data) == len_str:
				raise XHRPollingSocketException(
							"Data from %s to %s was not len %s (got %s)" %
							 (start_search, end_data, len_str, sub_data))
			messages.append( sub_data  )
	
			start = end_data
	
		return messages

	@classmethod
	def connect_to_server(cls, host, port, username, password, is_secure=False,
						  resource=None, **kwargs):
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
			
			if r.status_code != 200 or r.text != cls.WS_CONNECT:
				raise XHRPollingSocketException(
								"Could not set connection to %s" % urlf)
			
			result = XHRPollingSocket()
			result.connect(urlf, auth)
			return result
		else:
			raise XHRPollingSocketException(
						"Invalid status code while posting to %s" % urlf)
	
	connect_to_ds = connect_to_server  # BWC

def create_server_connection(host, port, username, password, is_secure=False,
							 resource=None, **options):
	result = XHRPollingSocket.connect_to_server(host=host,
											 	port=port,
											 	username=username,
											 	password=password,
											 	is_secure=is_secure,
												resource=resource,
												**options)
	return result
