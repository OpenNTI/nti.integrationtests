

class SocketIOException(Exception):
	pass

class ConnectionClosedException(SocketIOException):
	pass

class SocketIOSocket(object):
	
	def __init__(self):
		self.connected = False

	def connect(self, url, *args, **kwargs):
		"""
		Connect to url.
		"""
		raise NotImplementedError()
		
	def send(self, payload):
		"""
		Send the data as string. payload must be utf-8 string or unicoce.
		"""
		raise NotImplementedError()

	def recv(self):
		"""
		Reeive utf-8 string data from the server.
		"""
		raise NotImplementedError()

	def close(self):
		"""
		Close Socket object
		"""
		raise NotImplementedError()

