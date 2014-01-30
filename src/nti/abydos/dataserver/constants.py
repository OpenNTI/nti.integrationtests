# -*- coding: utf-8 -*-
"""
Defines DataServer chat users.

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

WS_ACK			 = b'6::'
WS_CONNECT		 = b'1::'
WS_DISCONNECT	 = b'0::'
WS_MESSAGE		 = b'3::'
WS_BROADCAST	 = b'5:::'

SERVER_KILL		 = 'serverkill'

EVT_MESSAGE	 = 'message'
EVT_EXIT_ROOM = 'chat_exitRoom'
EVT_ENTER_ROOM = 'chat_enterRoom'
EVT_EXITED_ROOM = 'chat_exitedRoom'
EVT_ENTERED_ROOM = 'chat_enteredRoom'
EVT_SHADOW_USERS = 'chat_shadowUsers'
EVT_POST_MESSAGE = 'chat_postMessage'
EVT_RECV_MESSAGE = 'chat_recvMessage'
EVT_SET_PRESENCE = 'chat_setPresence'
EVT_APPROVE_MSGS = 'chat_approveMessages'
EVT_MAKE_MODERATED = 'chat_makeModerated'
EVT_RECV_MSG_SHADOW	 = 'chat_recvMessageForShadow'
EVT_FAILED_TO_ENTER_ROOM = 'chat_failedToEnterRoom'
EVT_ADD_OCCUPANT_TO_ROOM = 'chat_addOccupantToRoom'
EVT_ROOM_MEMBERSHIP_CHANGED = 'chat_roomMembershipChanged'
EVT_SET_PRESENCE_OF_USERS_TO = 'chat_setPresenceOfUsersTo'
EVT_RECV_MSG_4_MODERATION = 'chat_recvMessageForModeration'
EVT_PRESENCE_OF_USER_CHANGE_TO = 'chat_presenceOfUserChangedTo'

EVT_NOTICE_INCOMING_CHANGE = 'data_noticeIncomingChange'

DEAULT_TIMEOUT	 = 30
META_CHANNEL	 = 'META'
POLL_CHANNEL	 = 'POLL'
STATE_CHANNEL	 = 'STATE'
DEFAULT_CHANNEL	 = 'DEFAULT'
WHISPER_CHANNEL	 = 'WHISPER'
CONTENT_CHANNEL	 = 'CONTENT'

CHANNELS = (DEFAULT_CHANNEL, WHISPER_CHANNEL, META_CHANNEL, CONTENT_CHANNEL,
			POLL_CHANNEL, STATE_CHANNEL)
