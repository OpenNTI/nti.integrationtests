#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import uuid
import unittest
import threading

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.chat.objects import BasicUser

from nose.plugins.attrib import attr
from hamcrest import (assert_that, is_)

class _User(BasicUser):
	def __init__(self, change_type='Circled', *args, **kwargs):
		super(_User, self).__init__(*args, **kwargs)
		self.change_type = change_type
		self.found = False
	
	def data_noticeIncomingChange(self, change):
		self.found = change.get('ChangeType', None) == self.change_type
	
	def __call__(self, *args, **kwargs):
		try:
			self.ws_connect()
			self.heart_beats = 0
			while self.heart_beats <=5 and not self.found:
				self.nextEvent()
		except:
			pass
		finally:
			self.ws_close()

@attr(level=5)
class TestNotifications(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)
	
	def setUp(self):
		super(TestNotifications, self).setUp()
		self.ds.set_credentials(self.owner)

	def _delete_all_friends_lists(self, credentials):
		lists = self.ds.get_friends_lists(credentials=credentials)
		for fl in lists.values():
			self.ds.delete_object(fl, credentials=credentials)
		
	def test_circled_event(self):
		usr = self.ds.get_user_object(self.target[0], credentials=self.target)
		__traceback_info__ = usr
		usr.dynamicMemberships = usr.following = usr.communities = usr.accepting = []
		usr = self.ds.update_object(usr, credentials=self.target)
		
		self._delete_all_friends_lists(self.owner)
		self._delete_all_friends_lists(self.target)
		
		usr = _User(username=self.target[0], pasword=self.target[1], port=self.port)
		t = threading.Thread(target=usr)
		t.start()
		time.sleep(1)
		
		name = '%s-%s' % (str(uuid.uuid4()).split('-')[0], time.time())
		self.ds.create_friends_list_with_name_and_friends(name, friends=[self.target[0]])
		
		t.join()
		assert_that(usr.found, is_(True))


if __name__ == '__main__':
	unittest.main()
