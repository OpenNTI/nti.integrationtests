#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
websocket - WebSocket client library for Python

Copyright (C) 2010 Hiroki Ohtani(liris)

	This library is free software; you can redistribute it and/or
	modify it under the terms of the GNU Lesser General Public
	License as published by the Free Software Foundation; either
	version 2.1 of the License, or (at your option) any later version.

	This library is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
	Lesser General Public License for more details.

	You should have received a copy of the GNU Lesser General Public
	License along with this library; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

	https://github.com/liris/websocket-client/blob/master/websocket.py

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re
import md5
import base64
import random
import socket
import struct
from urlparse import urlparse

from ZODB import loglevels

from . import SocketIOSocket
from . import SocketIOException
from . import get_default_timeout
from . import ConnectionClosedException

__all__ = [	'WebSocketException', 'WebSocket', 'create_ds_connection']

def _parse_url(url):
	"""
	parse url and the result is tuple of
	(hostname, port, resource path and the flag of secure mode)
	"""
	parsed = urlparse(url)
	if parsed.hostname:
		hostname = parsed.hostname
	else:
		raise ValueError("hostname is invalid")
	port = 0
	if parsed.port:
		port = parsed.port

	is_secure = False
	if parsed.scheme == b"ws":
		if not port:
			port = 80
	elif parsed.scheme == b"wss":
		is_secure = True
		if not port:
			port = 443
	else:
		raise ValueError("scheme %s is invalid" % parsed.scheme)

	if parsed.path:
		resource = parsed.path
	else:
		resource = b"/"

	return (hostname, port, resource, is_secure)

_MAX_INTEGER = (1 << 32) - 1
_MAX_CHAR_BYTE = (1 << 8) - 1
_AVAILABLE_KEY_CHARS = range(0x21, 0x2f + 1) + range(0x3a, 0x7e+1)

# ref. Websocket gets an update, and it breaks stuff.
# http://axod.blogspot.com/2010/06/websocket-gets-update-and-it-breaks.html

def _create_sec_websocket_key():
	spaces_n = random.randint(1, 12)
	max_n = _MAX_INTEGER / spaces_n
	number_n = random.randint(0, int(max_n))

	product_n = number_n * spaces_n
	key_n = str(product_n)

	for _ in range(random.randint(1, 12)):
		c = random.choice(_AVAILABLE_KEY_CHARS)
		pos = random.randint(0, len(key_n))
		key_n = key_n[0:pos] + chr(c) + key_n[pos:]

	for _ in range(spaces_n):
		pos = random.randint(1, len(key_n) - 1)
		key_n = key_n[0:pos] + b" " + key_n[pos:]

	return number_n, key_n

def _create_key3():
	return b"".join([chr(random.randint(0, _MAX_CHAR_BYTE)) for _ in range(8)])

HEADERS_TO_CHECK = {b"upgrade": b"websocket", b"connection": b"upgrade", }

HEADERS_TO_EXIST_FOR_HYBI00 = [b"sec-websocket-origin", b"sec-websocket-location", ]

HEADERS_TO_EXIST_FOR_HIXIE75 = [b"websocket-origin", b"websocket-location", ]

class WebSocketException(SocketIOException):
	pass

class _SSLSocketWrapper(object):
	def __init__(self, sock):
		self.sock = sock
		self.ssl = socket.ssl(sock)

	def recv(self, bufsize):
		return self.ssl.read(bufsize)

	def send(self, payload):
		return self.ssl.write(payload)

	def settimeout(self, timeout):
		self.sock.settimeout(timeout)

	def connect(self, *args, **kwargs):
		self.sock.connect(*args, **kwargs)

class WebSocket(SocketIOSocket):
	"""
	Low level WebSocket interface.
	This class is based on
	  The WebSocket protocol draft-hixie-thewebsocketprotocol-76
	  http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76

	We can connect to the websocket server and send/recieve data.
	The following example is a echo client.

	>>> import websocket
	>>> ws = websocket.WebSocket()
	>>> ws.Connect("ws://localhost:8080/echo")
	>>> ws.send("Hello, Server")
	>>> ws.recv()
	'Hello, Server'
	>>> ws.close()
	"""

	WS_HEART_BEAT = b'2::'

	logging_level = loglevels.TRACE
	_msg_pat = re.compile(u'.+\\:15\\:10\\:.*websocket.*')

	def __init__(self, secure=False):
		"""
		Initalize WebSocket object.
		"""
		super(SocketIOSocket, self).__init__()
		self.connected = False
		self.io_sock = self.sock = socket.socket()
		if secure:
			self.io_sock = _SSLSocketWrapper(self.sock)

	def settimeout(self, timeout):
		"""
		Set the timeout to the websocket.
		"""
		self.sock.settimeout(timeout)

	def gettimeout(self):
		"""
		Get the websocket timeout.
		"""
		return self.sock.gettimeout()

	def connect(self, url, **options):
		"""
		Connect to url. url is websocket url scheme. ie. ws://host:port/resource
		"""
		host, port, resource, is_secure = _parse_url(url)
		self.sock.connect((host, port))
		self._handshake(host, port, resource, is_secure, **options)
		return self

	def _handshake(self, host, port, resource, is_secure, **options):

		if is_secure and not isinstance(self.io_sock, _SSLSocketWrapper):
			self.io_sock = _SSLSocketWrapper(self.sock)

		sock = self.io_sock
		ws_info = list()

		ws_info.append(b"GET %s HTTP/1.1" % bytes(resource))
		ws_info.append(b"Upgrade: WebSocket")
		ws_info.append(b"Connection: Upgrade")
		if port == 80:
			hostport = host
		else:
			hostport = b"%s:%d" % (host, port)

		ws_info.append(b"Host: %s" % hostport)
		ws_info.append(b"Origin: %s" % hostport)

		number_1, key_1 = _create_sec_websocket_key()
		ws_info.append(b"Sec-WebSocket-Key1: %s" % key_1)
		number_2, key_2 = _create_sec_websocket_key()
		ws_info.append(b"Sec-WebSocket-Key2: %s" % key_2)

		if "headers" in options:
			ws_info.extend(options["headers"])

		ws_info.append(b"")
		key_3 = _create_key3()
		ws_info.append(key_3)

		header_str = b"\r\n".join(ws_info)
		sock.send(header_str)

		logger.log(self.logging_level, "--- request header ---")
		logger.log(self.logging_level, header_str)
		logger.log(self.logging_level, "-----------------------")

		status, resp_headers = self._read_headers()
		if status != 101:
			self.close()
			raise WebSocketException("Handshake Status %d" % status)

		success, secure = self._validate_header(resp_headers)
		if not success:
			self.close()
			raise WebSocketException("Invalid WebSocket Header")

		if secure:
			resp = self._get_resp()
			if not self._validate_resp(number_1, number_2, key_3, resp):
				self.close()
				raise WebSocketException("challenge-response error")

		self.connected = True

	def _validate_resp(self, number_1, number_2, key3, resp):
		challenge = struct.pack(b"!I", number_1)
		challenge += struct.pack(b"!I", number_2)
		challenge += key3
		digest = md5.md5(challenge).digest()
		return resp == digest

	def _get_resp(self):
		result = self._recv(16)
		logger.log(self.logging_level, "--- challenge response result ---")
		logger.log(self.logging_level, repr(result))
		logger.log(self.logging_level, "---------------------------------")

		return result

	def _validate_header(self, headers):
		# TODO: check other headers
		for key, value in HEADERS_TO_CHECK.iteritems():
			v = headers.get(key, None)
			if value != v:
				return False, False

		success = 0
		for key in HEADERS_TO_EXIST_FOR_HYBI00:
			if key in headers:
				success += 1
		if success == len(HEADERS_TO_EXIST_FOR_HYBI00):
			return True, True
		elif success != 0:
			return False, True

		success = 0
		for key in HEADERS_TO_EXIST_FOR_HIXIE75:
			if key in headers:
				success += 1
		if success == len(HEADERS_TO_EXIST_FOR_HIXIE75):
			return True, False

		return False, False

	def _read_headers(self):
		status = None
		headers = {}
		logger.log(self.logging_level, "--- response header ---")

		while True:
			line = self._recv_line()
			if line == b"\r\n":
				break
			line = line.strip()
			logger.log(self.logging_level, line)
			if not status:
				status_info = line.split(" ", 2)
				status = int(status_info[1])
			else:
				kv = line.split(":", 1)
				if len(kv) == 2:
					key, value = kv
					headers[key.lower()] = value.strip().lower()
				else:
					raise WebSocketException("Invalid header")

		logger.log(self.logging_level, "-----------------------")

		return status, headers

	def send(self, payload):
		"""
		Send the data as string. payload must be utf-8 string or unicoce.
		"""
		if isinstance(payload, unicode):
			payload = payload.encode("utf-8")
		data = b"".join([b"\x00", payload, b"\xff"])
		self.io_sock.send(data)

		logger.log(self.logging_level, "send: " + repr(data))

	def recv(self):
		"""
		Reeive utf-8 string data from the server.
		"""
		b = self._recv(1)
		logger.log(self.logging_level, "recv frame: " + repr(b))
		frame_type = ord(b)
		if frame_type == 0x00:
			_data = []
			while True:
				b = self._recv(1)
				if b == b"\xff":
					break
				else:
					_data.append(b)
			return "".join(_data)

		if 0x80 < frame_type < 0xff:
			# which frame type is valid?
			length = self._read_length()
			_data = self._recv_strict(length)
			return _data
		if frame_type == 0xff:
			self._recv(1)
			self._closeInternal()
			return None

		raise WebSocketException("Invalid frame type %s" % b)

	def _read_length(self):
		length = 0
		while True:
			b = ord(self._recv(1))
			length = length * (1 << 7) + (b & 0x7f)
			if b < 0x80:
				break

		return length

	def close(self):
		"""
		Close Websocket object
		"""
		if self.connected:
			try:
				self.io_sock.send(b"\xff\x00")
				timeout = self.sock.gettimeout()
				self.sock.settimeout(1)
				try:
					result = self._recv(2)
					if result != b"\xff\x00":
						logger.log(self.logging_level,
								  "bad closing Handshake %s" % result)
				except:
					pass
				self.sock.settimeout(timeout)
				self.sock.shutdown(socket.SHUT_RDWR)
			except:
				pass
		self._closeInternal()

	def _closeInternal(self):
		self.connected = False
		self.sock.close()
		self.io_sock = self.sock

	def _recv(self, bufsize):
		_data = self.io_sock.recv(bufsize)
		if not _data:
			raise ConnectionClosedException()
		return _data

	def _recv_strict(self, bufsize):
		remaining = bufsize
		_data = ""
		while remaining:
			_data += self._recv(remaining)
			remaining = bufsize - len(_data)

		return _data

	def _recv_line(self):
		line = []
		while True:
			c = self._recv(1)
			line.append(c)
			if c == b"\n":
				break
		return "".join(line)

	def _recv_till_found(self, word):
		line = []
		while True:
			c = self._recv(1)
			line.append(c)
			if len(line) >= len(word):
				s = b"".join(line)
				if word in s:
					return s
		return None

	def heartbeat(self):
		return self.send(self.WS_HEART_BEAT)

	def isHeartBeat(self, msg):
		return str(msg).startswith(self.WS_HEART_BEAT)

	@classmethod
	def connect_to_server(cls, host, port, username, password, is_secure=False,
					  	  timeout=None, resource=None, **kwargs):
		host = bytes(host)
		resource = resource or b'/socket.io/1/'
		resource = resource + b'/' if resource[-1] != b'/' else resource

		ws = WebSocket(is_secure)
		ws.settimeout(timeout or get_default_timeout())
		io_sock = ws.io_sock
		io_sock.connect((host, port))

		base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
		auth_header = b'Authorization: Basic %s' % base64string

		# socket.io handshake
		io_sock.send(b'POST %s HTTP/1.1\r\n' % resource)
		io_sock.send(auth_header)
		io_sock.send(b'\r\nContent-Length: 0\r\n')
		io_sock.send(b'\r\n')

		status, resp_headers = ws._read_headers()
		if status == 200:
			cl = resp_headers['content-length'] \
				 if 'content-length' in resp_headers else None
			if cl:
				content_length = int(resp_headers['content-length'])

				# get the session id. the server returns the session id e.g.
				# 57e45c8578d9426fb0f12336c5ef21:15:10:websocket,xhr-polling
				# 5ac894738a704995bd846dcad606e1:15:10:flashsocket,websocket,xhr-polling
				msg = ws._recv_strict(content_length)
				if cls._msg_pat.match(msg):
					sessiond_id = msg.split(":")[0]
					resource = b'%s%s/%s' % (resource, 'websocket', sessiond_id)

					header = kwargs.get('headers', [])
					header.append(auth_header)
					kwargs['headers'] = header

					ws._handshake(host, port, resource, is_secure, **kwargs)
					return ws
				else:
					ws.close()
					raise WebSocketException(
							"Could not find session id in server reply '%s'" % msg)
			else:
				ws.close()
				raise WebSocketException("Invalid server response")
		else:
			ws.close()
			raise WebSocketException("Invalid status %s writing to %s (%s)" %
									 (status, resource, resp_headers))
	connect_to_ds = connect_to_server  # BWC

def create_server_connection(host, port, username, password, is_secure=False,
							 timeout=None, resource=None, **options):
	result = WebSocket.connect_to_server(host=host,
									 	 port=port,
									 	 username=username,
									 	 password=password,
									 	 is_secure=is_secure,
										 timeout=timeout,
										 resource=resource,
										 **options)
	return result

create_ds_connection = create_server_connection
