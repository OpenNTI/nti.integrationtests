#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import random
import unittest

from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from nose.plugins.attrib import attr

@attr(priority=5, type='chat')
class TestMultiUserChat(HostUserChatTest):
	
	chatting_users = 4
	
	def setUp(self):
		super(TestMultiUserChat, self).setUp()
		self.chat_users = self.user_names[:self.chatting_users]
	
	def test_multiuser_chat(self):
		entries = random.randint(5, 10)
		users = self._run_chat(self.container, entries, *self.chat_users)
		
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		for i in range(len(users) -1):
			self._compare_mu_msgs(users[i], users[i+1])
			self._compare_mu_msgs(users[i+1], users[i])
		
	def _compare_mu_msgs(self, sender, receiver):
		
		_sent = list(sender.sent)
		self.assertTrue(len(_sent) > 0, "%s did not send any messages" % sender)
		
		_recv = list(receiver.received)
		self.assertTrue(len(_recv) > 0, "%s did not get any messages" % receiver)
		
		for s in _sent:
			self.assert_(s in _recv, "%s did not get message '%s' from %s" % (receiver, s, sender))
	
if __name__ == '__main__':
	unittest.main()
