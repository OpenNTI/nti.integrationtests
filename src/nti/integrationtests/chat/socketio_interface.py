from __future__ import print_function, unicode_literals

import six
import json
import plistlib
import threading
import collections
from collections import OrderedDict, Mapping

from nti.integrationtests.contenttypes import toExternalObject

from nti.integrationtests.socketio import SocketIOException
from nti.integrationtests.socketio import ConnectionClosedException

from nti.integrationtests.socketio.websocket import WebSocket
from nti.integrationtests.socketio.xhrpolling import XHRPollingSocket

WS_ACK			= b'6::'
WS_CONNECT		= b'1::'
WS_DISCONNECT	= b'0::'
WS_HEART_BEAT	= b'2::'
WS_MESSAGE		= b'3::'
WS_BROADCAST	= b'5:::'

SERVER_KILL		= 'serverkill'

EVT_MESSAGE			= 'message'
EVT_EXIT_ROOM		= 'chat_exitRoom'
EVT_ENTER_ROOM		= 'chat_enterRoom'
EVT_EXITED_ROOM		= 'chat_exitedRoom'
EVT_ENTERED_ROOM	= 'chat_enteredRoom'
EVT_SHADOW_USERS	= 'chat_shadowUsers'
EVT_POST_MESSAGE	= 'chat_postMessage'
EVT_RECV_MESSAGE	= 'chat_recvMessage'
EVT_MAKE_MODERATED	= 'chat_makeModerated'
EVT_APPROVE_MSGS	= 'chat_approveMessages'
EVT_RECV_MSG_SHADOW = 'chat_recvMessageForShadow'
EVT_RECV_MSG_MOD	= 'chat_recvMessageForModeration'
EVT_ROOM_MEMBERSHIP_CHANGED = "chat_roomMembershipChanged"
EVT_PRESENCE_OF_USER_CHANGE_TO = 'chat_presenceOfUserChangedTo'

EVT_NOTICE_INCOMING_CHANGE = 'data_noticeIncomingChange'

DEFAULT_CHANNEL = 'DEFAULT'
WHISPER_CHANNEL	= 'WHISPER'
META_CHANNEL	= 'META'
CONTENT_CHANNEL = 'CONTENT'
POLL_CHANNEL	= 'POLL'
DEFAULT_USER_PASSWORD = 'temp001'
DEAULT_TIMEOUT = 180

CHANNELS = (DEFAULT_CHANNEL, WHISPER_CHANNEL, META_CHANNEL, CONTENT_CHANNEL, POLL_CHANNEL)

class BasicMessageContext(object):

	def __init__(self):
		self._last_sent = None
		self._last_recv = None

	def recv(self, ws):
		self._last_recv = ws.recv()
		return self._last_recv

	def send(self, ws, msg):
		msg = unicode(msg)
		ws.send(msg)
		self._last_sent = msg
		return self._last_sent

	def reset(self):
		self._last_sent = None
		self._last_recv = None

	@property
	def sent(self):
		return [self._last_sent] if self._last_sent else []

	@property
	def received(self):
		return [self._last_recv] if self._last_recv else []

	@property
	def last_recv(self):
		return self._last_recv

	@property
	def last_sent(self):
		return self._last_sent

class MessageContext(BasicMessageContext):
	def __init__(self):
		super(MessageContext, self).__init__()
		self._sent=[]
		self._recv=[]

	def recv(self, ws):
		msg = super(MessageContext, self).recv(ws)
		self._recv.append(msg)
		return msg

	def send(self, ws, msg):
		msg = super(MessageContext, self).send(ws, msg)
		self._sent.append(msg)
		return msg

	def reset(self):
		self._sent=[]
		self._recv=[]

	@property
	def sent(self):
		return self._sent

	@property
	def received(self):
		return self._recv

class ThreadLocalMessageContext(threading.local, MessageContext):
	def __init__(self):
		MessageContext.__init__(self)

default_message_context = ThreadLocalMessageContext()


def _nonefy(s):
	return None if s and str(s) == 'null' else s

def _create_message_body(info):
	if isinstance(info, six.string_types):
		body = [info]
	elif isinstance(info, list):
		body = [toExternalObject(m) for m in info]
	else:
		body = [toExternalObject(info) or info]
	return body

class _Room():
	def __init__(self, **kwargs):

		ID = kwargs.get('ID', kwargs.get('id', None))
		active = kwargs.get('Active', kwargs.get('active', True))
		occupants = kwargs.get('Occupants', kwargs.get('occupants', None))
		moderated = kwargs.get('Moderated',  kwargs.get('moderated', False))
		containerId = kwargs.get('ContainerId',  kwargs.get('containerId', None))

		assert ID, ("must specify a valid room ID", kwargs)
		assert occupants != None, ("must specify valid room occupants", kwargs)

		self.ID = ID
		self.active = active
		self.occupants = occupants
		self.moderated = moderated
		self.containerId = containerId

	def __str__(self):
		return self.ID

	def __repr__(self):
		return "<%s,%s,%s,%s,%s>" % (self.ID, self.occupants, self.active, self.moderated, self.containerId)

	def __eq__( self, other ):
		if isinstance(other, six.string_types):
			return self.ID == other
		if isinstance(other, _Room):
			return self.ID == other.ID

		return False


class _Message(object):
	def __init__(self, **kwargs):
		self.ID = kwargs.get('ID', None)
		self.message = kwargs['message']
		self.inReplyTo = kwargs.get('inReplyTo', None)
		self.recipients = kwargs.get('recipients', None)
		self.channel = kwargs.get('channel', DEFAULT_CHANNEL)
		self.creator = kwargs.get('Creator', kwargs.get('creator',None))
		self.containerId = kwargs.get('ContainerId', kwargs.get('containerId',None))

	@property
	def content(self):
		return self.message

	@property
	def text(self):
		if self.message:
			if isinstance(self.message, list):
				return str(self.message[0])
			else:
				return str(self.message)
		else:
			return None

	def __str__(self):
		return self.message

	def __repr__(self):
		return "<%r,%r>" % (self.__class__.__name__, self.message)

class _RecvMessage(_Message):
	def __init__(self, **kwargs):
		super(_RecvMessage, self).__init__(**kwargs)
		self.lastModified = kwargs.get('lastModified', 0)

	def __eq__( self, other ):
		if isinstance(other, six.string_types):
			return self.ID == other
		elif isinstance(other, _RecvMessage):
			return self.ID == other.ID
		else:
			return False

	def __repr__(self):
		return "<%s,%s,%s,%s>" % (self.__class__.__name__, self.ID, self.creator, self.message)

class _PostMessage(_Message):
	def __init__(self, **kwargs):
		super(_PostMessage, self).__init__(**kwargs)

	def __eq__( self, other ):
		if isinstance(other, six.string_types):
			return str(self.message) == other
		elif isinstance(other, _PostMessage):
			return self.message == other.message
		else:
			return False

class DSUser(object):

	def __init__(self, *args, **kwargs):

		self.rooms = {}
		self.sent_messages = []
		self.recv_messages = OrderedDict()
		self.shadowed_messages = OrderedDict()
		self.moderated_messages = OrderedDict()

		self.ws_sent = None
		self.ws_recv = None
		self.killed = False
		self.heart_beats = 0
		self.is_secure = kwargs.get('is_secure', False) 
		self.transport = kwargs.get('transport', 'websocket')
		self.message_context = kwargs.get('message_context', MessageContext())

		self.ws = kwargs.get('ws', None)
		self.host = kwargs.get('host', None)
		self.port = kwargs.get('port', 8081)
		self.timeout = kwargs.get('timeout', DEAULT_TIMEOUT)
		self.username = kwargs.get('username', None)
		self.password = kwargs.get('password', DEFAULT_USER_PASSWORD)
		self.data_format = kwargs.get('data_format', 'json')
		self.connected = getattr(self.ws, "connected", False) if self.ws else False

		self.timeout = self.timeout
		self.data_format = self.data_format or 'json'

	# ---- --------- ----

	@property
	def sent(self):
		for m in self.sent_messages:
			yield m.text

	@property
	def received(self):
		for m in self.recv_messages.itervalues():
			yield m.text

	@property
	def moderated(self):
		for m in self.moderated_messages.itervalues():
			yield m.text

	@property
	def shadowed(self):
		for m in self.shadowed_messages.itervalues():
			yield m.text

	def sent_on_channel(self, channel=DEFAULT_CHANNEL):
		for m in self.sent_messages:
			if m.channel == channel:
				yield m

	def received_on_channel(self, channel=DEFAULT_CHANNEL):
		for m in self.recv_messages.itervalues():
			if m.channel == channel:
				yield m

	def get_sent_messages(self, clear=False):
		result = list(self.sent_messages)
		if clear: self.sent_messages.clear()
		return result

	def get_received_messages(self, clear=False):
		return self._get_and_clear(self.recv_messages, clear)

	def get_shadowed_messages(self, clear=False):
		return self._get_and_clear(self.shadowed_messages, clear)

	def get_moderated_messages(self, clear=False):
		return self._get_and_clear(self.moderated_messages, clear)

	def _get_and_clear(self, messages, clear=False):
		result = list(messages.itervalues())
		if clear: messages.clear()
		return result

	# ---- Callbacks ----

	def serverKill(self, args=None):
		self.killed = True
		self.connected = False

	def connect(self):
		self.connected = True

	def disconnect(self):
		self.connected = False

	def heartBeat(self):
		self.connected = True
		self.heart_beats += 1

	def enterRoom(self, **kwargs):
		d = dict(kwargs)
		d['data_format'] = self.data_format
		d['message_context'] = self.message_context
		return _enterRoom(self.ws, **d)

	def exitRoom( self, room_id ):
		if room_id in self.rooms:
			_exitRoom(self.ws, room_id, self.data_format, message_context=self.message_context)
			return self.rooms.pop(room_id, None)
		else:
			return None

	def makeModerated(self, containerId, flag=True):
		_makeModerated(self.ws, containerId, flag, self.data_format, message_context=self.message_context)

	def approveMessages(self, mids):
		_approveMessages(self.ws, mids, self.data_format, message_context=self.message_context)

	def shadowUsers(self, containerId, users):
		_shadowUsers(self.ws, containerId, users, self.data_format, message_context=self.message_context)

	chat_exitRoom = exitRoom
	chat_enterRoom = enterRoom
	chat_shadowUsers = shadowUsers
	chat_makeModerated = makeModerated
	chat_approveMessage = approveMessages

	# ---- ----- ----

	def chat_roomMembershipChanged(self, room_info):
		pass

	def chat_presenceOfUserChangedTo(self, username, status):
		pass

	def chat_exitedRoom(self, **kwargs):
		ID = kwargs.get('ID', kwargs.get('id', None))
		occupants = kwargs.get('Occupants', kwargs.get('occupants', []))
		if not self.username in occupants:
			return self.rooms.pop(ID, None) if ID else None
		else:
			room = _Room(**kwargs)
			self.rooms[ID] = room
			return room

	def chat_enteredRoom(self, **kwargs):
		room = _Room(**kwargs)
		self.rooms[room.ID] = room
		return room

	def chat_postMessage(self, **kwargs):
		d = dict(kwargs)
		if not 'creator' in d:
			d['creator'] = self.username
		d['message_context'] = self.message_context
		d['message'] = _create_message_body(kwargs['message'])
		_postMessage(ws=self.ws, data_format=self.data_format, **d)

		post_msg = _PostMessage(**d)
		self.sent_messages.append(post_msg)
		return post_msg

	postMessage = chat_postMessage

	def send_heartbeat(self):
		_send_heartbeat(self.ws)
		
	# ---- ----- ----
	
	def data_noticeIncomingChange(self, change):
		pass
		
	# ---- ----- ----

	def _msg_params(self, **kwargs):
		return {'message'		: kwargs['Body'],
				'ID'			: kwargs['ID'],
				'containerId'	: kwargs['ContainerId'],
				'creator'		: kwargs['Creator'],
				'channel'		: kwargs.get('channel', DEFAULT_CHANNEL),
				'lastModified'	: kwargs.get('Last Modified', 0),
				'inReplyTo'		: _nonefy(kwargs.get('inReplyTo', None)),
				'recipients'	: _nonefy(kwargs.get('recipients', None)) }

	def chat_recvMessage(self, **kwargs):
		d = self._msg_params(**kwargs)
		message = _RecvMessage(**d)
		self.recv_messages[d['ID']] = message
		return message

	def chat_recvMessageForModeration(self, **kwargs):
		d = self._msg_params(**kwargs)
		message = _RecvMessage(**d)
		self.moderated_messages[d['ID']] = message
		return message

	def chat_recvMessageForShadow(self, **kwargs):
		d = self._msg_params(**kwargs)
		message = _RecvMessage(**d)
		self.shadowed_messages[d['ID']] = message
		return message

	recvMessage = chat_recvMessage
	recvMessageForModeration = chat_recvMessageForModeration

	# ---- ----- ----

	def runLoop(self):
		self.killed = False
		try:
			if not self.ws:
				self.ws_connect()
			else:
				self.connected = getattr(self.ws, "connected", False)

			while self.connected or not self.killed:
				self.nextEvent()
		except ConnectionClosedException:
			pass
		finally:
			self.ws_capture()

	def nextEvent(self):
		return _next_event(self.ws, self, message_context=self.message_context)

	# ---- WebSocket ----

	def ws_connect(self):

		if self.ws_connected:
			self.ws.close()

		self.ws = _ws_connect(self.host, self.port, username=self.username,
							  password=self.password, timeout=self.timeout,
							  is_secure=self.is_secure,
							  transport=self.transport,
							  message_context=self.message_context)

		self.connected = getattr(self.ws, "connected", False)

	def ws_close(self):
		if self.ws_connected:
			try:
				_ws_disconnect(self.ws, message_context=self.message_context)
				self.ws.close()
			finally:
				self.ws = None
				self.connected = False

	def ws_capture(self, reset=True):
		self.ws_sent = list(self.message_context.sent)
		self.ws_recv = list(self.message_context.received)
		if reset:
			self.message_context.reset()

	def ws_capture_and_close(self, reset=True):
		self.ws_capture(reset=reset)
		self.ws_close()

	@property
	def ws_connected(self):
		return getattr(self.ws, "connected", False) if self.ws else False

	@property
	def ws_last_recv(self):
		return self.message_context.last_recv

	@property
	def ws_last_sent(self):
		return self.message_context.last_sent

Graph = DSUser


def _self_of_emtpy(s):
	return ' ' + s if s else ''

class Serverkill(SocketIOException):
	def __init__(self, args=None):
		super(Serverkill, self).__init__(str(args) if args else '')

class InvalidAuthorization(SocketIOException):
	def __init__(self, username, password=''):
		super(InvalidAuthorization, self).__init__('Invalid credentials for %s' % username)
		self.username = username
		self.password = password

class InvalidDataFormat(SocketIOException):
	def __init__(self, data_format=''):
		super(InvalidDataFormat, self).__init__('Invalid data format %s' % data_format)
		self.data_format = data_format

class CouldNotEnterRoom(SocketIOException):
	def __init__(self, room_id=None):
		super(CouldNotEnterRoom, self).__init__('Could not enter room' + _self_of_emtpy( room_id))

class NotEnoughOccupants(SocketIOException):
	def __init__(self, room_id=''):
		super(NotEnoughOccupants, self).__init__('room %s does not have enough occupants' % room_id)

class InActiveRoom(SocketIOException):
	def __init__(self, room_id=''):
		super(InActiveRoom, self).__init__('Room is inactive %s' % room_id)

# -----------------------------

def toList(data, unique=True):
	if data:
		if isinstance(data, six.string_types) or not isinstance(data, collections.Iterable):
			data = [data]
		elif not isinstance(data, list):
			data = list(set(data)) if unique else list(data)
	return data

def isConnect(msg):
	return str(msg).startswith(WS_CONNECT)

def isBroadCast(msg):
	return str(msg).startswith(WS_BROADCAST)

def isHeartBeat(msg):
	return str(msg).startswith(WS_HEART_BEAT)

def encode(data, data_format='json'):
	result = None
	if data_format == 'json':
		result = json.dumps(data)
	elif data_format == 'plist':
		result = plistlib.writePlistToString(data)
	return unicode(result) if result else None

def decode(msg, data_format='json'):
	if msg and msg.startswith(WS_BROADCAST):
		msg = msg[len(WS_BROADCAST):]
		if data_format == 'json':
			return json.loads(msg)
		elif data_format == 'plist':
			return plistlib.readPlistFromString(msg)
	return None

def isEvent(data, event, data_format='json'):
	if isinstance(data, six.string_types):
		data = decode(data, data_format)
	if isinstance(data, Mapping):
		return data.get('name',None) == event
	return False

def isServerKill(data, data_format='json'):
	return isEvent(data, SERVER_KILL, data_format)

def isRecvMessage(data, data_format='json'):
	return isEvent(data, EVT_RECV_MESSAGE, data_format)

def isExitedRoom(data, data_format='json'):
	return isEvent(data, EVT_EXITED_ROOM, data_format)

def isEnteredRoom(data, data_format='json'):
	return isEvent(data, EVT_ENTERED_ROOM, data_format)

def isPresenceOfUserChangedTo(data, data_format='json'):
	return isEvent(data, EVT_PRESENCE_OF_USER_CHANGE_TO, data_format)

def isRoomMembershipChanged(data, data_format='json'):
	return isEvent(data, EVT_ROOM_MEMBERSHIP_CHANGED, data_format)

def isRecv4Moderation(data, data_format='json'):
	return isEvent(data, EVT_RECV_MSG_MOD, data_format)

def isRecvMessageForShadow(data, data_format='json'):
	return isEvent(data, EVT_RECV_MSG_SHADOW, data_format)

def isApproveMessages(data, data_format='json'):
	return isEvent(data, EVT_APPROVE_MSGS, data_format)

def isDataIncomingChange(data, data_format='json'):
	return isEvent(data, EVT_NOTICE_INCOMING_CHANGE, data_format)
	
def _next_event(ws, graph=None, message_context=default_message_context):
	msg = message_context.recv(ws)
	if graph and isinstance(graph, DSUser):
		if isConnect(msg):
			graph.connect()
		elif isHeartBeat(msg):
			graph.heartBeat()
		elif isBroadCast(msg):
			d = decode(msg)
			if isServerKill(d):
				graph.serverKill(args=d.get('args', None))
			elif isEnteredRoom(d) or isExitedRoom(d):

				entered = isEnteredRoom(d)
				params = d['args'][0]

				if entered:
					graph.chat_enteredRoom(**params)
				else:
					graph.chat_exitedRoom(**params)

			elif isRecvMessage(d) or isRecv4Moderation(d) or isRecvMessageForShadow(d):
				moderated = isRecv4Moderation(d)
				shadow = isRecvMessageForShadow(d)

				params = d['args'][0]

				if moderated:
					graph.chat_recvMessageForModeration(**params)
				elif shadow:
					graph.chat_recvMessageForShadow(**params)
				else:
					graph.chat_recvMessage(**params)

			elif isPresenceOfUserChangedTo(d):
				d = d['args']
				graph.chat_presenceOfUserChangedTo(username=d[0], status=d[1])

			elif isRoomMembershipChanged(d):
				room_info = d['args'][0]
				graph.chat_roomMembershipChanged(room_info)
			elif isDataIncomingChange(d):
				change = d['args'][0]
				graph.data_noticeIncomingChange(change)

	return msg

def _exitRoom(ws, containerId, data_format='json', message_context=default_message_context):
	d = {"name":EVT_EXIT_ROOM, "args":[containerId]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

def _enterRoom(ws, **kwargs):

	message_context = kwargs.get('message_context', default_message_context)

	occupants = kwargs.get('occupants', kwargs.get('Occupants',None))
	inReplyTo = kwargs.get("inReplyTo", None)
	references = kwargs.get("references", None)
	containerId = kwargs.get("containerId", kwargs.get("ContainerId", None))

	data_format = kwargs.get("data_format", 'json')

	assert containerId, 'must specify either valid container id'

	args = {"Occupants": occupants}
	if containerId:
		args["ContainerId"] = containerId

	if inReplyTo:
		args["inReplyTo"] = inReplyTo

	if references:
		args["references"] = references

	d = {"name":EVT_ENTER_ROOM, "args":[args]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

	return (None, None)

def _postMessage(ws, **kwargs):

	message = kwargs['message']
	inReplyTo = kwargs.get("inReplyTo", None)
	recipients = kwargs.get("recipients", None)
	channel = kwargs.get("channel", DEFAULT_CHANNEL)
	containerId = kwargs.get("containerId", kwargs.get("ContainerId", None))

	assert containerId,'must specify a valid container'

	data_format = kwargs.get("data_format", 'json')
	message_context = kwargs.get('message_context', default_message_context)

	args = {"ContainerId": containerId, "Body": message, "Class":"MessageInfo"}
	if channel and channel != DEFAULT_CHANNEL:
		args['channel'] = channel

	if recipients:
		args['recipients'] = recipients

	if inReplyTo:
		args['inReplyTo'] = inReplyTo

	d = {"name":EVT_POST_MESSAGE, "args":[args]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

def _makeModerated(ws, containerId, flag=True, data_format='json', message_context=default_message_context):

	d = {"name":EVT_MAKE_MODERATED, "args":[containerId, flag]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

def _approveMessages(ws, mids, data_format='json', message_context=default_message_context):
	mids = toList(mids)
	d = {"name":EVT_APPROVE_MSGS, "args":[mids]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

def _shadowUsers(ws, containerId, users, data_format='json', message_context=default_message_context):
	users = toList(users)
	d = {"name":EVT_SHADOW_USERS, "args":[containerId, users]}
	msg = encode(d, data_format)
	if msg:
		msg = WS_BROADCAST + msg
		message_context.send(ws, msg)
	else:
		raise InvalidDataFormat(data_format)

def _ws_disconnect(ws, data_format='json', message_context=default_message_context):
	msg = b"0::"
	message_context.send(ws, msg)

def _send_heartbeat(ws):
	ws.send(WS_HEART_BEAT)

def _ws_connect(host, port, username, password=DEFAULT_USER_PASSWORD, is_secure=False,
				transport='websocket', timeout=DEAULT_TIMEOUT, message_context=default_message_context):

	if transport == 'xhr-polling':
		result = XHRPollingSocket.connect_to_ds(host, port, username, password, is_secure)
	else:
		result = WebSocket.connect_to_ds(host, port, username, password, is_secure, timeout)
	return result

if __name__ == "__main__":
	ws = _ws_connect('localhost', 8081, 'test.user.1@nextthought.com', 'temp001')
	_next_event(ws)
	_ws_disconnect(ws)
	ws.close()
