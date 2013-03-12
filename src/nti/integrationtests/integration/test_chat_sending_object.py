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

from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import CanvasAffineTransform

from hamcrest import ( has_entry, assert_that, has_length )

from nose.plugins.attrib import attr

@attr(priority=5, type='chat')
class TestChatSendingObject(HostUserChatTest):
	
	def setUp(self):
		super(TestChatSendingObject, self).setUp()
		
		self.user_one = self.user_names[0]
		self.user_two = self.user_names[1]
		self.user_three = self.user_names[2]
		
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials((self.user_one, self.default_user_password))
		
		transform = CanvasAffineTransform(a=0, b=0, c=0, d=0, tx=.25, ty=.25)
		polygon = CanvasPolygonShape(sides=4, transform=transform, container=self.container)
		canvas = Canvas(shapeList=[polygon], container=self.container)
		created_obj = self.ds.create_object(canvas, adapt=True)
		
		self.host_messages = [u'A note to user', created_obj]
	
	def test_chat_sending_obj(self):
		users = self._run_chat(self.container, 1, self.user_one, self.user_two)
		for u in users:
			self.assert_(u.exception == None, "User %s caught exception '%s'" % (u.username, u.traceback))

		messages = list(users[1].received_on_channel())
		assert_that(messages, has_length(2))
		
		for m in messages:
			content = m.content
			if isinstance(content, list):
				content = content[0]
			if isinstance(content, dict):
				assert_that(content, has_entry('MimeType', u'application/vnd.nextthought.canvas'))
	
	def _create_host(self, username, occupants, **kwargs):
		return Host(self.host_messages, username=username, occupants=occupants, port=self.port, **kwargs)
	
# ----------------------------
	
class Host(objects.Host):
		
	def __init__(self, host_messages, *args, **kwargs):
		super(Host, self).__init__(*args, **kwargs)
		self.host_messages = host_messages
		
	def post_messages(self, room_id, tick=5, *args, **kwargs):
		counter = 0
		for m in self.host_messages:
			counter += 1
			self.chat_postMessage(message=m, containerId=room_id)
			time.sleep(0.25)
			if counter % tick == 0:
				self.send_heartbeat()
	
if __name__ == '__main__':
	unittest.main()
