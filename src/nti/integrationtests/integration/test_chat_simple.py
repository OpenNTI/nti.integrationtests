#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import random
import unittest

from nti.integrationtests.utils import DEFAULT_USER_PASSWORD
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from hamcrest import (assert_that, has_length, greater_than, greater_than_or_equal_to)

from nose.plugins.attrib import attr

@attr(priority=5, type='chat')
class TestSimpleChat(HostUserChatTest):

	@classmethod
	def static_initialization(cls):
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		cls.create_users(create_friends_lists=False, ds_client=ds_client)

		cls.user_one = cls.user_names[0]
		cls.user_two = cls.user_names[1]
		cls.user_three = cls.user_names[2]
		
		fls = []
		fls.append((cls.user_one, cls.register_friends(cls.user_one, [cls.user_two], ds_client=ds_client)))
		fls.append((cls.user_two, cls.register_friends(cls.user_two, [cls.user_one], ds_client=ds_client)))
		fls.append((cls.user_three, cls.register_friends(cls.user_three, [cls.user_one, cls.user_two], ds_client=ds_client)))

		cls.user_four = cls.user_names[3]
		fls.append((cls.user_four, cls.register_friends(cls.user_four, [cls.user_one, cls.user_two], ds_client=ds_client)))

		cls.user_five = cls.generate_user_name()
		cls.friend_lists = fls
	
	@classmethod
	def static_finalization(cls):
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		for username, fl in cls.friend_lists:
			ds_client.set_credentials(user=username, password=DEFAULT_USER_PASSWORD)
			ds_client.delete_object(fl)
		
	def test_simple_chat(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, self.user_one, self.user_two)

		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare_sc_msgs(users[i], users[i+1])
			self._compare_sc_msgs(users[i+1], users[i])

	def test_chat_user_not_friend(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, self.user_three, self.user_four)

		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare_sc_msgs(users[i], users[i+1])
			self._compare_sc_msgs(users[i+1], users[i])

	def test_chat_unregistered_user(self):
		entries = random.randint(5, 10)
		one, two = self._run_chat(self.container, entries, self.user_one, self.user_five)
		self.assert_(len(one.users_online) == 0, "No user was supposed to be online")
		self.assert_(two.exception, "Invalid Auth was expected for %s" % two.username)

	def _compare_sc_msgs(self, sender, receiver):
		_sent = list(sender.sent)
		assert_that( _sent, has_length( greater_than( 0 ) ), "%s did not send any messages" % sender)

		_recv = list(receiver.received)
		assert_that( _recv, has_length( greater_than( 0 ) ), "%s did not get any messages" % receiver)

		assert_that( _recv, has_length( greater_than_or_equal_to( len( _sent ) ) ),
						  "%s did not get all messages from %s" % (receiver, sender))

if __name__ == '__main__':
	unittest.main()
