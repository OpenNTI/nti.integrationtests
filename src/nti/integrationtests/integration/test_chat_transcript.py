#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest

from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from hamcrest import (is_in, assert_that, is_, has_entry, not_none, has_property, has_key)

from nose.plugins.attrib import attr

@attr(level=5, type='chat')
class TestChatTranscript(HostUserChatTest):

	def setUp(self):
		super(TestChatTranscript, self).setUp()
		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]

	def test_chat_transcript(self):
		entries = 50
		one, two = self._run_chat(self.container, entries, self.user_one, self.user_two, delay=0.5)
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
			assert_that( body, is_( not_none() ) )
			assert_that( m, has_entry( 'ID', not_none() ) )
			assert_that( m, has_property( 'container', room_id ) )
			assert_that( m, has_property( 'status', 'st_POSTED' ) )
			assert_that( body, is_in( all_msgs ) )

		# flag last message
		m = self.ds.flag_object(m)
		assert_that(m.get_flag_metoo_link(), not_none())

if __name__ == '__main__':
	unittest.main()
