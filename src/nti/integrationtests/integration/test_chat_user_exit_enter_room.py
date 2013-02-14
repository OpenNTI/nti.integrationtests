#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import unittest

from nti.integrationtests.chat import objects
from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

#from hamcrest import (is_, assert_that, has_length, greater_than_or_equal_to )

@unittest.SkipTest
class TestChatUserExitEnterRoom(HostUserChatTest):

	def setUp(self):
		super(TestChatUserExitEnterRoom, self).setUp()
		self.chat_users = self.user_names[:4]
		self.exit_enter_user = self.chat_users[-1]

	def test_chat_room_renter(self):
		entries = 2
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

	def _create_user(self, username, **kwargs):
		exit_enter = username == self.exit_enter_user
		return User(exit_enter=exit_enter, username=username, port=self.port, **kwargs)

	def _create_host(self, username, occupants, **kwargs):
		return Host(username=username, occupants=occupants, port=self.port, **kwargs)

class Host(objects.Host):
	
	total_sent = 0
	
	def post_messages(self, room_id, entries, *args, **kwargs):
		self.total_sent = 0
		for _ in range(2):
			self.post_random_messages(room_id, entries, tick=1)
			self.wait_heart_beats(2)
			self.total_sent += entries

class User(objects.User):
	
	def __init__(self, exit_enter=False, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.total_sent = 0
		self._exit_event = None
		self._renter_event = None
		self.exit_enter = exit_enter

	def post_messages(self, room_id, entries, *args, **kwargs):
		for _ in range(3):
			self.post_random_messages(room_id, entries, tick=2)
			self.wait_heart_beats(1)
			self.total_sent += entries
		
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
				delay = kwargs.get('delay', 0.05)
				entries = kwargs.get('entries', None)
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
					self._exit_event.wait(10)
					
					if self.room is not None:
						raise Exception('%s did not exit the chat room' % self.username)
					
					time.sleep(3)  # wait a bit before rejoining
					
					self._renter_event = event.__class__()
					self.enterRoom(RoomId=room_id)
					self._renter_event.wait(10)
					
					if self.room is None:
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
