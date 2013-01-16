#import requests

from collections import deque

from nti.integrationtests.socketio import SocketIOSocket
from nti.integrationtests.socketio import SocketIOException

import logging
logger = logging.getLogger(__name__)

class XHRPollingSocketException(SocketIOException):
	pass

class XHRPollingSocket(SocketIOSocket):
	
	def __init__(self):
		super(SocketIOSocket, self).__init__()
		self.queue = deque([])

