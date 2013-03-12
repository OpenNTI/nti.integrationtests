#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import random
import unittest

from nti.integrationtests.chat.objects import Host

from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from nose.plugins.attrib import attr

@attr(priority=5, type='chat')
class TestModeratedChat(HostUserChatTest):

	def setUp(self):
		super(TestModeratedChat, self).setUp()
		self.chat_users = self.user_names[:3]

	def test_moderated_chat(self):

		entries = random.randint(10, 15)
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		moderator = users[0]
		chatters = users[1:]

		all_recv=set()
		for c in chatters:
			msgs = c.recv_messages
			self.assert_(len(msgs) > 0, "User %s did not get any message" % c.username)
			map(lambda x: all_recv.add(x), msgs.iterkeys())

		for m in all_recv:
			self.assert_(m not in moderator.moderated_messages, "Moderated message %s was received by a user" % m)

	def _create_host(self, username, occupants, **kwargs):
		return Moderator(username=username, occupants=occupants, port=self.port, **kwargs)

class Moderator(Host):

	def chat_recvMessageForModeration(self, **kwargs):
		super(Moderator, self).chat_recvMessageForModeration(**kwargs)
		self.heart_beats = 0
		mid = kwargs['ID']
		if random.random() > 0.7:
			self.approveMessages(mid)
			self.moderated_messages.pop(mid , None)

	def wait_4_room(self):
		super(Moderator, self).wait_4_room()
		self.makeModerated(self.room)

	def post_messages(self, room_id, *args, **kwargs):
		pass

if __name__ == '__main__':
	unittest.main()
