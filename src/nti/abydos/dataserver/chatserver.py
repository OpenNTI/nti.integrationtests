# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from collections import OrderedDict

from . import protocol
from .. import alias, make_repr
from .constants import DEFAULT_CHANNEL

DEAULT_TIMEOUT = 30

class Room(object):

	id = alias('ID')
	active = alias('Active')
	occupants = alias('Occupants')
	moderated = alias('Moderated')
	containerId = alias('ContainerId')

	def __init__(self, ID=None, Occupants=None, Active=True, Moderated=False,
				 ContainerId=None, **kwargs):

		assert ID, "must specify a valid room ID"
		assert Occupants != None, "must specify valid room occupants"

		self.ID = ID
		self.Active = Active
		self.Occupants = Occupants
		self.Moderated = Moderated
		self.ContainerId = ContainerId

	def __str__(self):
		return self.ID

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or self.ID == other.ID
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.ID)
		return xhash

_Room = Room  # BWC

class Message(object):

	id = alias('ID')
	content = alias('message')

	def __init__(self, ID=None, message=None, channel=DEFAULT_CHANNEL, inReplyTo=None,
				 recipients=None, creator=None, lastModified=None, containerId=None,
				 **kwargs):
		self.ID = ID
		self.creator = creator
		self.message = message
		self.inReplyTo = inReplyTo
		self.recipients = recipients
		self.containerId = containerId
		self.channel = channel or DEFAULT_CHANNEL

	@property
	def text(self):
		result = None
		if isinstance(self.message, (list, tuple)):
			result = unicode(self.message[0]) if self.message else None
		elif self.message:
			result = unicode(self.message)
		return result

	def __str__(self):
		return str(self.message)

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or self.ID == other.ID
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.ID)
		return xhash

_Message = Message  # BWC

class RecvMessage(_Message):

	def __init__(self, **kwargs):
		super(_RecvMessage, self).__init__(**kwargs)
		self.lastModified = kwargs.get('lastModified', 0)

_RecvMessage = RecvMessage  # BWC

class PostMessage(_Message):
	pass

_PostMessage = PostMessage  # BWC

class Client(object):

	def __init__(self, transport=None, timeout=DEAULT_TIMEOUT, * args, **kwargs):
		self.reset()

		self.ws_sent = None
		self.ws_recv = None
		self.killed = False
		self.heart_beats = 0
		self.timeout = timeout
		self.transport = transport
		self.connected = getattr(self.transport, "connected", False)

	def reset(self):
		self.rooms = {}
		self.sent_messages = []
		self.recv_messages = OrderedDict()
		self.shadowed_messages = OrderedDict()
		self.moderated_messages = OrderedDict()

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

	# ---- 
	
	def enterRoom(self, Occupants=None, inReplyTo=None, references=None,
			  	  RoomId=None, ContainerId=None, **kwargs):
		result = protocol.enterRoom(Occupants=Occupants, inReplyTo=inReplyTo,
									references=references, RoomId=RoomId,
									ContainerI=ContainerId,
									transport=self.transport)
		return result

	def chat_enteredRoom(self, **kwargs):  # callback
		room = Room(**kwargs)
		self.rooms[room.ID] = room
		return room

	def exitRoom(self, roomId):
		if roomId in self.rooms:
			result = protocol.exitRoom(roomId=roomId, transport=self.transport)
			return result

	def chat_exitedRoom(self, **kwargs):  # callback
		ID = kwargs.get('ID')
		result = self.rooms.pop(ID, None) if ID else None
		return result

# 	def get_sent_messages(self, clear=False):
# 		result = list(self.sent_messages)
# 		if clear: self.sent_messages.clear()
# 		return result
#
# 	def get_received_messages(self, clear=False):
# 		return self._get_and_clear(self.recv_messages, clear)
#
# 	def get_shadowed_messages(self, clear=False):
# 		return self._get_and_clear(self.shadowed_messages, clear)
#
# 	def get_moderated_messages(self, clear=False):
# 		return self._get_and_clear(self.moderated_messages, clear)
#
# 	def _get_and_clear(self, messages, clear=False):
# 		result = list(messages.itervalues())
# 		if clear: messages.clear()
# 		return result
#
# 	# ---- Callbacks ----
#
# 	def serverKill(self, args=None):
# 		self.killed = True
# 		self.connected = False
#
# 	def connect(self):
# 		self.connected = True
#
# 	def disconnect(self):
# 		self.connected = False
#
# 	def heartBeat(self):
# 		self.connected = True
# 		self.heart_beats += 1
#
#
# 	def makeModerated(self, containerId, flag=True):
# 		_makeModerated(self.ws, containerId, flag, self.data_format, message_context=self.message_context)
#
# 	def approveMessages(self, mids):
# 		_approveMessages(self.ws, mids, self.data_format, message_context=self.message_context)
#
# 	def shadowUsers(self, containerId, users):
# 		_shadowUsers(self.ws, containerId, users, self.data_format, message_context=self.message_context)
#
# 	chat_shadowUsers = shadowUsers
# 	chat_makeModerated = makeModerated
# 	chat_approveMessage = approveMessages
#
# 	# ---- ----- ----
#
# 	def chat_roomMembershipChanged(self, room_info):
# 		pass
#
# 	def chat_setPresenceOfUsersTo(self, username, presenceInfo):
# 		pass
#
# 	def chat_presenceOfUserChangedTo(self, username, status):
# 		pass
#
# 	def chat_addOccupantToRoom(self, **kwargs):
# 		pass
#
# 	def chat_failedToEnterRoom(self, **kwargs):
# 		pass
#
# 	def chat_postMessage(self, **kwargs):
# 		d = dict(kwargs)
# 		if not 'creator' in d:
# 			d['creator'] = self.username
# 		d['message_context'] = self.message_context
# 		d['message'] = _create_message_body(kwargs['message'])
# 		_postMessage(ws=self.ws, data_format=self.data_format, **d)
#
# 		post_msg = _PostMessage(**d)
# 		self.sent_messages.append(post_msg)
# 		return post_msg
#
# 	postMessage = chat_postMessage
#
# 	def chat_setPresence(self, **kwargs):
# 		d = dict(kwargs)
# 		d['message_context'] = self.message_context
# 		if 'type' not in d:
# 			d['type'] = 'available'
# 		if 'show' not in d:
# 			d['show'] = 'chat'
# 		if 'username' not in d:
# 			d['username'] = self.username
# 		_setPresence(ws=self.ws, data_format=self.data_format, **d)
#
# 	setPresence = chat_setPresence
#
# 	def send_heartbeat(self):
# 		_send_heartbeat(self.ws)
#
# 	# ---- ----- ----
#
# 	def data_noticeIncomingChange(self, change):
# 		pass
#
# 	# ---- ----- ----
#
# 	def _msg_params(self, **kwargs):
# 		return {'message'		: kwargs['Body'],
# 				'ID'			: kwargs['ID'],
# 				'containerId'	: kwargs['ContainerId'],
# 				'creator'		: kwargs['Creator'],
# 				'channel'		: kwargs.get('channel', DEFAULT_CHANNEL),
# 				'lastModified'	: kwargs.get('Last Modified', 0),
# 				'inReplyTo'		: _nonefy(kwargs.get('inReplyTo', None)),
# 				'recipients'	: _nonefy(kwargs.get('recipients', None)) }
#
# 	def chat_recvMessage(self, **kwargs):
# 		d = self._msg_params(**kwargs)
# 		message = _RecvMessage(**d)
# 		self.recv_messages[d['ID']] = message
# 		return message
#
# 	def chat_recvMessageForModeration(self, **kwargs):
# 		d = self._msg_params(**kwargs)
# 		message = _RecvMessage(**d)
# 		self.moderated_messages[d['ID']] = message
# 		return message
#
# 	def chat_recvMessageForShadow(self, **kwargs):
# 		d = self._msg_params(**kwargs)
# 		message = _RecvMessage(**d)
# 		self.shadowed_messages[d['ID']] = message
# 		return message
#
# 	recvMessage = chat_recvMessage
# 	recvMessageForModeration = chat_recvMessageForModeration
#
# 	# ---- ----- ----
#
# 	def runLoop(self):
# 		self.killed = False
# 		try:
# 			if not self.ws:
# 				self.ws_connect()
# 			else:
# 				self.connected = getattr(self.ws, "connected", False)
#
# 			while self.connected or not self.killed:
# 				self.nextEvent()
# 		except ConnectionClosedException:
# 			pass
# 		finally:
# 			self.ws_capture()
#
# 	def nextEvent(self):
# 		return _next_event(self.ws, self, message_context=self.message_context)
#
# 	# ---- WebSocket ----
#
# 	def ws_connect(self):
#
# 		if self.ws_connected:
# 			self.ws.close()
#
# 		self.ws = _ws_connect(self.host, self.port, username=self.username,
# 							  password=self.password, timeout=self.timeout,
# 							  is_secure=self.is_secure,
# 							  transport=self.transport,
# 							  message_context=self.message_context)
#
# 		self.connected = getattr(self.ws, "connected", False)
#
# 	def ws_close(self):
# 		if self.ws_connected:
# 			try:
# 				_ws_disconnect(self.ws, message_context=self.message_context)
# 				self.ws.close()
# 			finally:
# 				self.ws = None
# 				self.connected = False
#
# 	def ws_capture(self, reset=True):
# 		self.ws_sent = list(self.message_context.sent)
# 		self.ws_recv = list(self.message_context.received)
# 		if reset:
# 			self.message_context.reset()
#
# 	def ws_capture_and_close(self, reset=True):
# 		self.ws_capture(reset=reset)
# 		self.ws_close()
#
# 	@property
# 	def ws_connected(self):
# 		return getattr(self.ws, "connected", False) if self.ws else False
#
# 	@property
# 	def ws_last_recv(self):
# 		return self.message_context.last_recv
#
# 	@property
# 	def ws_last_sent(self):
# 		return self.message_context.last_sent
