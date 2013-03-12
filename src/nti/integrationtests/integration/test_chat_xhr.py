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
class TestSimpleChatXHR(HostUserChatTest):

	host_transport = 'xhr-polling'
	user_transport = 'xhr-polling'

	@classmethod
	def static_initialization(cls):
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		cls.create_users(create_friends_lists=False, ds_client=ds_client)

		cls.user_one = cls.user_names[0]
		cls.user_two = cls.user_names[1]
		cls.friendlist = cls.register_friends(cls.user_one, [cls.user_two], ds_client=ds_client)
	
	@classmethod
	def static_finalization(cls):
		ds_client = DataserverClient(endpoint = cls.resolve_endpoint(port=cls.port))
		ds_client.set_credentials(user=cls.user_one, password=DEFAULT_USER_PASSWORD)
		ds_client.delete_object(cls.friendlist)
		
	def test_xhr_chat(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, self.user_one, self.user_two)

		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare(users[i], users[i+1])
			self._compare(users[i+1], users[i])

	def _compare(self, sender, receiver):
		_sent = list(sender.sent)
		assert_that( _sent, has_length( greater_than( 0 ) ), "%s did not send any messages" % sender)

		_recv = list(receiver.received)
		assert_that( _recv, has_length( greater_than( 0 ) ), "%s did not get any messages" % receiver)

		assert_that( _recv, has_length( greater_than_or_equal_to( len( _sent ) ) ),
					"%s did not get all messages from %s" % (receiver, sender))
		
if __name__ == '__main__':
	unittest.main()
