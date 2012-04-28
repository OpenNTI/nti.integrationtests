#!/usr/bin/env python
from __future__ import unicode_literals
import unittest

from hamcrest import assert_that, is_, has_entry, not_none, has_property, has_key
from hamcrest import is_in

from user_chat_objects import HostUserChatTest

class TestChatTranscript(HostUserChatTest):

	def setUp(self):
		super(TestChatTranscript, self).setUp()

		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]

	def test_transcript(self):

		entries = 50
		one, two = self._run_chat(self.container, entries, self.user_one, self.user_two)
		for u in (one, two):
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		assert_that( one, has_property( 'room', not_none() ), "User '%s' could not enter room" % one.username)
		assert_that( two, has_property( 'room', not_none() ), "User '%s' could not enter room" % two.username)

		room_id = two.room

		all_msgs = []
		map(all_msgs.append, one.sent)
		map(all_msgs.append, one.received)

		self.ds.set_credentials(user=one.username, password=one.password)
		t = self.ds.get_transcript(self.container, room_id)

		assert_that( t, has_key( 'RoomInfo' ) )

		ri = t['RoomInfo']
		assert_that( ri, has_property( 'id', room_id ) )
		assert_that( ri, has_property( 'messageCount', entries * 2) )
		assert_that( t, has_key( 'Messages' ) )

		messages = t['Messages']
		for m in messages:
			body = m['Body'][0]
			assert_that( m, has_key( 'ID' ) )
			assert_that( body, is_( not_none() ) )
			assert_that( m, has_entry( 'ContainerId', room_id ) )
			assert_that( m, has_entry( 'Status', 'st_POSTED' ) )
			assert_that( body, is_in( all_msgs ) )


if __name__ == '__main__':
	unittest.main()
