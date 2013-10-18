#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import unittest

from nti.integrationtests.chat import objects
from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from nose.plugins.attrib import attr
from hamcrest import (assert_that, is_, has_length)

@attr(level=5, type='chat')
class TestChatReEnterRoom(HostUserChatTest):

	def setUp(self):
		super(TestChatReEnterRoom, self).setUp()
		self.chat_users = self.user_names[:3]
		self.exit_enter_user = self.chat_users[-1]

	def test_chat_room_renter(self):
		users = self._run_chat(self.container, 2, *self.chat_users)
		sent_array = [10, 6, 4] # 
		recv_array = [10, 14]
		for i, u in enumerate(users):
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))
			assert_that(u.total_sent, is_(sent_array[i]))
			if i < len(recv_array):
				assert_that(list(u.received), has_length(recv_array[i]))

	def _create_user(self, username, **kwargs):
		exit_enter = username == self.exit_enter_user
		return User(exit_enter=exit_enter, username=username, port=self.port, **kwargs)

	def _create_host(self, username, occupants, **kwargs):
		return Host(username=username, occupants=occupants, port=self.port, **kwargs)

class _BaseUser(object):
	delay = 1.2
	to_send = 5
	total_sent = 0

class Host(_BaseUser, objects.Host):
	
	def post_messages(self, room_id, *args, **kwargs):
		self.total_sent = 0
		for _ in range(2):
			self.post_random_messages(room_id, self.to_send, delay=self.delay, tick=1)
			self.total_sent += self.to_send

class User(_BaseUser, objects.User):
	
	to_send = 3
	
	def __init__(self, exit_enter=False, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self._exit_event = None
		self._renter_event = None
		self.exit_enter = exit_enter

	def post_messages(self, room_id, *args, **kwargs):
		for _ in range(2):
			self.post_random_messages(room_id, self.to_send, delay=self.delay, tick=1)
			self.total_sent += self.to_send
		
	def chat_enteredRoom(self, **kwargs):
		super(User, self).chat_enteredRoom(**kwargs)
		if self._renter_event:
			self._renter_event.set()
	
	def chat_exitedRoom(self, **kwargs):
		super(User, self).chat_exitedRoom(**kwargs)
		if self._exit_event:
			self._exit_event.set()
		
	def __call__(self, *args, **kwargs):
		if not self.exit_enter:
			super(User, self).__call__(*args, **kwargs)
		else:
			try:
				entries = 2
				delay = kwargs.get('delay', 0.05)
				max_heart_beats = kwargs.get('max_heart_beats', 2)
	
				# connect
				self.ws_connect()
				event = kwargs.get('connect_event', None)
				event.wait(20)
				self.wait_4_room()
	
				room_id = self.room
				if room_id:
					self.post_random_messages(room_id, entries, delay=delay)
					self.total_sent += entries
										
					self._exit_event = event.__class__()
					self.exitRoom(room_id)
					now = time.time()
					while not self._exit_event.is_set() and (time.time() - now < 30):
						self.nextEvent()
					
					if not self._exit_event.is_set():
						raise Exception('%s did not exit the chat room' % self.username)
					
					time.sleep(2)  # wait a bit before rejoining
					
					self._renter_event = event.__class__()
					self.enterRoom(RoomId=room_id)
					now = time.time()
					while not self._renter_event.is_set() and (time.time() - now < 30):
						self.nextEvent()
					
					if not self._renter_event.is_set():
						raise Exception('%s did not renter the chat room' % self.username)
					
					self.post_random_messages(room_id, entries, delay=delay)
					self.total_sent += entries 
				else:
					raise Exception('%s did not enter a chat room' % self.username)
	
				# get any message
				self.wait_heart_beats(max_heart_beats)
	
			except Exception, e:
				self.save_traceback(e)
			finally:
				self.ws_capture_and_close()

if __name__ == '__main__':
	unittest.main()
