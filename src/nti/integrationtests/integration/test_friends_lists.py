#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import uuid
import unittest
	
from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import accepting
from nti.integrationtests.integration import containing_friend
from nti.integrationtests.integration import containing_friends
from nti.integrationtests.integration import containing_no_friends
from nti.integrationtests.integration import contains_friendslist
from nti.integrationtests.integration import friends_list_from_friends_lists

from hamcrest import (is_not, has_key, assert_that)

from nose.plugins.attrib import attr

@attr(priority=3)
class TestBasicFriendsLists(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	friend = ('test.user.3@nextthought.com',DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicFriendsLists, self).setUp()
		self.ds.set_credentials(self.owner)
		uid = str(uuid.uuid4()).split('-')[0]
		self.list_name = '%s-%s@nextthought.com' % (uid, time.time())

	def create_friends_list_with_name_and_friends(self, name, friends):
		return self.ds.create_friends_list_with_name_and_friends(name, friends)
	
	def test_can_create_empty_friendslist(self):
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, [])
		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_no_friends(friendsList))

		self.ds.delete_object(createdlist)

	def test_can_create_duplicate_friendslist(self):
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, [])
		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		try:
			createdlist_2 = self.create_friends_list_with_name_and_friends(self.list_name, [])
			self.ds.delete_object(createdlist_2)
			self.fail('Created a duplicate friend list')
		except:
			pass
	
		self.ds.delete_object(createdlist)
		
	def test_can_delete_friendslist(self):
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))

		self.ds.delete_object(createdlist)
		lists = self.ds.get_friends_lists()
		assert_that(lists, is_not(contains_friendslist(self.list_name)))

	def test_can_create_friendslist_with_friends(self):
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))

		self.ds.delete_object(createdlist)

	def test_can_delete_from_friendslist(self):
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))

		friendsList.friends = [friends[0]]
		self.ds.update_object(friendsList)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friend(friendsList, friends[0]))
		assert_that(not containing_friend(friendsList, friends[1]))

		self.ds.delete_object(createdlist)

	def test_can_add_to_friendslists(self):
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, [])

		lists = self.ds.get_friends_lists()
		assert_that(lists, has_key(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_no_friends(friendsList))

		createdlist.friends = [friends[0]]
		createdlist = self.ds.update_object(createdlist)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friend(friendsList, friends[0]))

		createdlist.friends = friends
		createdlist = self.ds.update_object(createdlist)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))

		self.ds.delete_object(createdlist)

	def test_circling_causes_acceptance(self):
		createdlist = self.create_friends_list_with_name_and_friends(self.list_name, [self.friend[0]])

		friends_user_object = self.ds.get_user_object(credentials=self.friend)
		assert_that(accepting(friends_user_object, self.owner[0]))

		self.ds.delete_object(createdlist)

if __name__ == '__main__':
	unittest.main()
