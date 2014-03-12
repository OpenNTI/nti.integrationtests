#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import uuid
import random
import unittest

from nti.integrationtests.chat.objects import Host
from nti.integrationtests.chat.objects import User

from nti.integrationtests.integration.user_chat_objects import HostUserChatTest

from nose.plugins.attrib import attr

@attr(level=5, type='chat')
class TestModeratedChat(HostUserChatTest):

	def setUp(self):
		super(TestModeratedChat, self).setUp()
		self.chat_users = self.user_names[:3]

	def _create_user(self, username, **kwargs):
		return Chatter(username=username, port=self.port, **kwargs)
	
	def test_moderated_chat(self):
		entries = random.randint(10, 15)
		users = self._run_chat(self.container, entries, *self.chat_users)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		moderator = users[0]
		chatters = users[1:]

		credentials = (self.user_names[0], self.default_user_password)
		self.ds.process_hypatia(-1, credentials=credentials)

		all_recv=set()
		for c in chatters:
			msgs = c.recv_messages
			self.assert_(len(msgs) > 0, "User %s did not get any message" % c.username)
			map(lambda x: all_recv.add(x), msgs.iterkeys())

		for m in all_recv:
			self.assert_(m not in moderator.moderated_messages, "Moderated message %s was received by a user" % m)

		if not moderator.unmoderated:
			return
		text = moderator.unmoderated[0].text
		credentials = (self.user_names[1], self.default_user_password)
		self.ds.set_credentials(credentials)
		result = self.ds.search_user_content('"%s"' % text)
		self.assert_(result[u'Hit Count'] == 0, 'found unmoderated message')

	def _create_host(self, username, occupants, **kwargs):
		return Moderator(username=username, occupants=occupants, port=self.port, **kwargs)

class Chatter(User):
	def generate_message(self, *arg, **args):
		return unicode(str(uuid.uuid4()))

class Moderator(Host):

	def __init__(self, *args, **kwargs):
		super(Moderator, self).__init__(*args, **kwargs)
		self.unmoderated = []

	def chat_recvMessageForModeration(self, **kwargs):
		m = super(Moderator, self).chat_recvMessageForModeration(**kwargs)
		self.heart_beats = 0
		mid = kwargs['ID']
		if random.random() > 0.7:
			self.approveMessages(mid)
			self.moderated_messages.pop(mid , None)
		else:
			self.unmoderated.append(m)

	def wait_4_room(self):
		super(Moderator, self).wait_4_room()
		self.makeModerated(self.room)

	def post_messages(self, room_id, *args, **kwargs):
		pass

if __name__ == '__main__':
	unittest.main()
