# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from . import protocol

def runLoop(client, transport=None):
	client.killed = False
	while client.connected or not client.killed:
		nextEvent(transport, client)

run_loop = runLoop  # BWC

def nextEvent(transport, client):
	msg = transport.recv()
	if protocol.isConnect(msg):
		client.connect()
	elif transport.isHeartBeat(msg):
		client.heartBeat()
	elif client.isBroadCast(msg):
		d = protocol.decode(msg)
		if protocol.isServerKill(d):
			client.serverKill(args=d.get('args', None))
		elif protocol.isEnteredRoom(d):
			params = d['args'][0]
			client.chat_enteredRoom(**params)
		elif protocol.isExitedRoom(d):
			params = d['args'][0]
			client.chat_exitedRoom(**params)
		elif protocol.isAddOccupantToRoom(d):
			params = d['args'][0]
			client.chat_addOccupantToRoom(**params)
		elif protocol.isFailedToEnterRoom(d):
			params = d['args'][0]
			client.chat_failedToEnterRoom(**params)
		elif protocol.isRecvMessage(d) or protocol.isRecv4Moderation(d) or \
			 protocol.isRecvMessageForShadow(d):

			moderated = protocol.isRecv4Moderation(d)
			shadow = protocol.isRecvMessageForShadow(d)
			params = d['args'][0]

			if moderated:
				client.chat_recvMessageForModeration(**params)
			elif shadow:
				client.chat_recvMessageForShadow(**params)
			else:
				client.chat_recvMessage(**params)

		elif protocol.isPresenceOfUserChangedTo(d):
			d = d['args']
			client.chat_presenceOfUserChangedTo(username=d[0], status=d[1])
		elif protocol.isSetPresenceOfUsersTo(d):
			args = d['args']
			for data in args or ():
				for k, v in data.items():
					client.chat_setPresenceOfUsersTo(k, v)

		elif protocol.isRoomMembershipChanged(d):
			room_info = d['args'][0]
			client.chat_roomMembershipChanged(room_info)
		elif protocol.isDataIncomingChange(d):
			change = d['args'][0]
			client.data_noticeIncomingChange(change)

	return msg

next_event = _next_event = nextEvent # BWC
