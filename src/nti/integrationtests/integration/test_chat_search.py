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

@attr(level=5, type='chat')
class TestChatSearch(HostUserChatTest):
	
	def setUp(self):
		super(TestChatSearch, self).setUp()
					
		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]
		self.user_eight = self.user_names[8]
	
		self.host_messages = ("Yellow brown", "Blue red green render purple", "Every red town")
		self.user_messages = ("Three rendered four five.", "Preserving extreme", "Chicken hacker")
	
	def test_chat_search(self):
		
		users = self._run_chat(self.container, 0, self.user_one, self.user_two)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))
		
		credentials = (self.user_one, self.default_user_password)
		self.ds.process_hypatia(200, credentials=credentials)
		self.ds.set_credentials(credentials)
		
		user_1_host_snippet = self._get_snippet(self.ds.search_user_content("town"))
		user_1_user_snippet = self._get_snippet(self.ds.search_user_content("extreme"))

		self.assertEqual(user_1_host_snippet, 'Every red town', 'The host cant find his/her own message in search')
		self.assertEqual(user_1_user_snippet, 'Preserving extreme', 'The host cant find the users message in search')
		
		self.ds.set_credentials((self.user_two, self.default_user_password))
		
		user_2_host_snippet = self._get_snippet(self.ds.search_user_content("brown"))
		user_2_user_snippet = self._get_snippet(self.ds.search_user_content("chicken"))

		self.assertEqual(user_2_host_snippet, 'Yellow brown', 'The user cant find his/her own message in search')
		self.assertEqual(user_2_user_snippet, 'Chicken hacker', 'The user cant find the hosts message in search')
			
		self.ds.set_credentials((self.user_eight, self.default_user_password))
		
		user_3_host_snippet = self._get_snippet(self.ds.search_user_content("zankanotachi"))
		user_3_user_snippet = self._get_snippet(self.ds.search_user_content("benihime"))

		self.assertEqual(user_3_host_snippet, None, 'A user not involved in the chat found a message he shouldnt have')
		self.assertEqual(user_3_user_snippet, None, 'A user not involved in the chat found a message he shouldnt have')
		
	def _create_host(self, username, occupants, **kwargs):
		return Host(self.host_messages, username=username, occupants=occupants, port=self.port, **kwargs)
	
	def _create_user(self, username, **kwargs):
		return User(self.user_messages, username=username, port=self.port, **kwargs)
	
	def _get_snippet(self, result):
		latest = 0
		snippet = None
		items = result['Items']
		for d in items:
			if latest < int(d['Last Modified']):
				latest = int(d['Last Modified'])
				snippet = d['Snippet']
		return snippet
		
class Host(objects.Host):
		
	def __init__(self, host_messages, *args, **kwargs):
		super(Host, self).__init__(*args, **kwargs)
		self.host_messages = host_messages
		
	def post_messages(self, room_id, *args, **kwargs):
		for m in self.host_messages:
			self.chat_postMessage(message=unicode(m), containerId=room_id)
			time.sleep(0.25)
		
class User(objects.User):
		
	def __init__(self, user_messages, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.user_messages = user_messages
		
	def post_messages(self, room_id, *args, **kwargs):
		for m in self.user_messages:
			self.chat_postMessage(message=unicode(m), containerId=room_id)
			time.sleep(0.25)
					
if __name__ == '__main__':
	unittest.main()
