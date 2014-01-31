# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import json
from collections import Mapping

from . import to_list
from ..transports import SocketIOException
from .constants import (WS_CONNECT, WS_BROADCAST, SERVER_KILL, EVT_RECV_MESSAGE,
					    EVT_EXITED_ROOM, EVT_ENTERED_ROOM, EVT_ADD_OCCUPANT_TO_ROOM,
					    EVT_FAILED_TO_ENTER_ROOM, EVT_PRESENCE_OF_USER_CHANGE_TO,
					    EVT_SET_PRESENCE_OF_USERS_TO, EVT_ROOM_MEMBERSHIP_CHANGED,
					    EVT_RECV_MSG_4_MODERATION, EVT_RECV_MSG_SHADOW, EVT_APPROVE_MSGS,
					    EVT_NOTICE_INCOMING_CHANGE, EVT_EXIT_ROOM, EVT_ENTER_ROOM,
					    DEFAULT_CHANNEL, EVT_SET_PRESENCE, EVT_POST_MESSAGE,
					    EVT_MAKE_MODERATED, EVT_SHADOW_USERS, WS_DISCONNECT)

class Serverkill(SocketIOException):

	def __init__(self, args=None):
		super(Serverkill, self).__init__(str(args) if args else '')

class InvalidAuthorization(SocketIOException):

	def __init__(self, username, password=''):
		SocketIOException.__init__(self, 'Invalid credentials for %s' % username)
		self.username = username
		self.password = password

class CouldNotEnterRoom(SocketIOException):

	def __init__(self, rid=None):
		SocketIOException.__init__(self, 'Could not enter room %s' % rid or u'')

class NotEnoughOccupants(SocketIOException):

	def __init__(self, rid=''):
		SocketIOException.__init__(self, 'Room %s does not have enough occupants' % rid)

class InActiveRoom(SocketIOException):

	def __init__(self, rid=''):
		SocketIOException.__init__(self, 'Room is inactive %s' % rid)

def isConnect(msg):
	return str(msg).startswith(WS_CONNECT)

def isBroadCast(msg):
	return str(msg).startswith(WS_BROADCAST)

def encode(data):
	result = json.dumps(data) if data else None
	return unicode(result) if result else None

def decode(msg):
	if msg and msg.startswith(WS_BROADCAST):
		msg = msg[len(WS_BROADCAST):]
		return json.loads(msg)
	return None

def isEvent(data, event):
	if isinstance(data, six.string_types):
		data = decode(data)
	if isinstance(data, Mapping):
		return data.get('name', None) == event
	return False

def isServerKill(data):
	return isEvent(data, SERVER_KILL)

def isRecvMessage(data):
	return isEvent(data, EVT_RECV_MESSAGE)

def isExitedRoom(data):
	return isEvent(data, EVT_EXITED_ROOM)

def isEnteredRoom(data):
	return isEvent(data, EVT_ENTERED_ROOM)

def isAddOccupantToRoom(data):
	return isEvent(data, EVT_ADD_OCCUPANT_TO_ROOM)

def isFailedToEnterRoom(data):
	return isEvent(data, EVT_FAILED_TO_ENTER_ROOM)

def isPresenceOfUserChangedTo(data):
	return isEvent(data, EVT_PRESENCE_OF_USER_CHANGE_TO)

def isSetPresenceOfUsersTo(data):
	return isEvent(data, EVT_SET_PRESENCE_OF_USERS_TO)

def isRoomMembershipChanged(data):
	return isEvent(data, EVT_ROOM_MEMBERSHIP_CHANGED)

def isRecv4Moderation(data):
	return isEvent(data, EVT_RECV_MSG_4_MODERATION)

def isRecvMessageForShadow(data):
	return isEvent(data, EVT_RECV_MSG_SHADOW)

def isApproveMessages(data):
	return isEvent(data, EVT_APPROVE_MSGS)

def isDataIncomingChange(data):
	return isEvent(data, EVT_NOTICE_INCOMING_CHANGE)

def exitRoom(transport, ContainerId):
	d = {"name":EVT_EXIT_ROOM, "args":[ContainerId]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def enterRoom(transport, Occupants=None, inReplyTo=None, references=None,
			  RoomId=None, ContainerId=None):

	assert ContainerId or RoomId, 'must specify either valid container id or room id'

	args = {}
	if RoomId:
		args["RoomId"] = RoomId

	if Occupants:
		args["Occupants"] = Occupants

	if ContainerId:
		args["ContainerId"] = ContainerId

	if inReplyTo:
		args["inReplyTo"] = inReplyTo

	if references:
		args["references"] = references

	d = {"name":EVT_ENTER_ROOM, "args":[args]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def setPresence(transport, username, ContainerId=None, status=None,
				show=None, Type=None, ** kwargs):

	args = {u"ContainerId": ContainerId,
			u"show": show,
			u"type": Type,
			u"username": username,
			u"status" : status,
			u"MimeType":u"application/vnd.nextthought.presenceinfo"}

	d = {"name":EVT_SET_PRESENCE, "args":[args]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def postMessage(transport, message, ContainerId=None, inReplyTo=None, recipients=None,
				channel=None, **kwargs):

	channel = channel or DEFAULT_CHANNEL
	assert ContainerId, 'must specify a valid container'

	args = {"ContainerId": ContainerId, "Body": message, "Class":"MessageInfo"}
	if channel and channel != DEFAULT_CHANNEL:
		args['channel'] = channel

	if recipients:
		args['recipients'] = recipients

	if inReplyTo:
		args['inReplyTo'] = inReplyTo

	d = {"name":EVT_POST_MESSAGE, "args":[args]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def makeModerated(transport, ContainerId, flag=True):
	d = {"name":EVT_MAKE_MODERATED, "args":[ContainerId, flag]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def approveMessages(transport, mids):
	mids = to_list(mids)
	d = {"name":EVT_APPROVE_MSGS, "args":[mids]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def shadowUsers(transport, ContainerId, users):
	users = to_list(users)
	d = {"name":EVT_SHADOW_USERS, "args":[ContainerId, users]}
	msg = WS_BROADCAST + encode(d)
	transport.send(msg)
	return msg

def disconnect(transport):
	transport.send(WS_DISCONNECT)
	return WS_DISCONNECT

def send_heartbeat(transport):
	transport.heartbeat()

