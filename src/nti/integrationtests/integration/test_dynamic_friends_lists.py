#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains
from nti.integrationtests.integration import shared_with
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import containing_friends
from nti.integrationtests.integration import container_of_length

from nti.integrationtests.integration import test_friends_lists
from nti.integrationtests.integration import test_friends_sharing

from nose.plugins.attrib import attr
from hamcrest import (assert_that, is_, is_not, has_entry, greater_than_or_equal_to, has_length, none, greater_than)

@attr(level=3, type="dfl")
class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists,
							  test_friends_sharing.TestFriendsSharing):
	
	outsider = ('test.user.8', DataServerTestCase.default_user_password)
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()		
		self.realname ='%s@nt.com' % str(uuid.uuid4()).split('-')[-1]
		
	def create_friends_list_with_name_and_friends(self, name, friends, realname=None, locked=False):
		realname = realname or self.realname
		dfl = self.ds.create_DFL_with_name_and_friends(name, friends, realname=realname, locked=locked)
		return dfl
	
	def test_share_with_friends_and_delete_obj(self):
		self.ds.set_credentials(self.owner)

		# create friends list
		friends = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		# create and share
		created_obj = self.ds.create_note(self.note, container=self.container, sharedWith=[self.list_name])
		assert_that(created_obj, shared_with([friendsList.ntiid]))

		# check that the friends can now see it
		self._check_object_in_friends(created_obj, self.container, self.friends)
		self.ds.set_credentials(self.owner)

		# remove object
		self.ds.delete_object(created_obj)
		
		time.sleep(0.5) # wait till cache refresh in the server
		for f in self.friends:
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			user_data = self.ds.get_user_generated_data(self.container)
			assert_that(user_data, container_of_length(0))

		# clean up
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)
		
	def test_share_with_friends_and_remove_friend(self):
		# create friends list
		self.ds.set_credentials(self.owner)
		friends = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		# create and share
		created_obj = self.ds.create_note(self.note, container=self.container, sharedWith=[self.list_name])
		assert_that(created_obj, shared_with([friendsList.ntiid]))

		# check that the friends can now see it
		self._check_object_in_friends(created_obj, self.container, self.friends)
		self.ds.set_credentials(self.owner)

		# update friend list
		removedFriend = friends.pop()
		friendsList.friends = friends
		friendsList = self.ds.update_object(friendsList)
		assert_that(containing_friends(friendsList, friends))

		# check friends I shared w/ still can see the object
		friends = [(f, DataServerTestCase.default_user_password) for f in friends]
		self._check_object_in_friends(created_obj, self.container, friends)

		# check removed friend cannot see shared object
		time.sleep(0.5) # wait till cache refresh in the server
		self.ds.set_credentials(user=removedFriend, password=DataServerTestCase.default_user_password)
		user_data = self.ds.get_user_generated_data(self.container)
		assert_that(created_obj, is_not(contained_in(user_data)))
			
		# clean up
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)
		self.ds.delete_object(created_obj)
		
	def test_dfl_alpha_issue(self):
		# create friends list
		self.ds.set_credentials(self.owner)
		friend_names = [r[0] for r in self.friends]
		friendsList= self.create_friends_list_with_name_and_friends(self.list_name, friend_names)

		# create and share
		created_obj = self.ds.create_note(self.note, container=self.container, 
										  sharedWith=[self.list_name, self.outsider[0]])

		self.ds.set_credentials(self.outsider)
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj.id)
		
		try:
			#DFL ower should see the reply
			self.ds.set_credentials(self.owner)
			replies = self.ds.replies(created_obj)
			assert_that(replies, container_of_length(1))
			
			#outsider should see the reply
			self.ds.set_credentials(self.outsider)
			replies = self.ds.replies(created_obj)
			assert_that(replies, container_of_length(1))
			
			# members of the DFL should see the reply
			for f in self.friends:
				self.ds.set_credentials(f)
				replies = self.ds.replies(created_obj)
				assert_that(replies, container_of_length(1))
		finally:	
			self.ds.set_credentials(self.outsider)
			self.ds.delete_object(created_reply)
			
			# clean up
			self.ds.set_credentials(self.owner)
			self.ds.delete_object(friendsList)
			self.ds.delete_object(created_obj)
			
	def test_trello_846(self):
		self.ds.set_credentials(self.owner)
		friend_names = [r[0] for r in self.friends]
		friendsList= self.create_friends_list_with_name_and_friends(self.list_name, friend_names)

		created_obj = self.ds.create_note(u'Zanjutsu Gokui', container=self.container, sharedWith=[self.list_name])
		try:
			assert_that(created_obj, shared_with([friendsList.ntiid]))
			self.ds.process_hypatia(-1, credentials=self.owner)
			
			# all members can find note
			for fc in self.friends:
				self.ds.set_credentials(fc)
				content = self.ds.search_user_content("Zanjutsu")
				assert_that(content, has_entry('Hit Count', greater_than_or_equal_to(1)))
			
			# ower can find note
			self.ds.set_credentials(self.owner)
			content = self.ds.search_user_content("Gokui")
			assert_that(content, has_entry('Hit Count', greater_than_or_equal_to(1)))
		finally:	
			self.ds.set_credentials(self.owner)
			self.ds.delete_object(created_obj)
			self.ds.delete_object(friendsList)
			
	def test_trello_847(self):
		self.ds.set_credentials(self.owner)
		friend_name = self.friends[0][0]
		friendsList= self.create_friends_list_with_name_and_friends(self.list_name, [friend_name])

		#share w/ dfl
		note = self.ds.create_note(u'Two Kenpachis', container=self.container, sharedWith=[self.list_name])
		try:
			assert_that(note, shared_with([friendsList.ntiid]))
			
			# check note is in the stream 
			self.ds.set_credentials(self.friends[0])
			ugd = self.ds.get_user_generated_data(self.container)			
			assert_that(ugd, contains(note))

			# update note # direct share
			self.ds.set_credentials(self.owner)
			note.shareWith([friend_name], reset=True)
			note = self.ds.update_object(note)
			
			# check note is in the stream 
			self.ds.set_credentials(self.friends[0])
			ugd = self.ds.get_user_generated_data(self.container)			
			assert_that(ugd, contains(note))
		finally:	
			self.ds.set_credentials(self.owner)
			self.ds.delete_object(note)
			self.ds.delete_object(friendsList)

	def test_dfl_user_search(self):
		self.ds.set_credentials(self.owner)
		friend_names = [r[0] for r in self.friends]
		suffix = str(uuid.uuid4()).split('-')[-1]
		flname = "bankai-%s" % suffix
		friendsList= self.create_friends_list_with_name_and_friends(flname, friend_names, flname)

		# make sure we have a link to get the code when the DFL is not locked
		link = friendsList.get_link('default-trivial-invitation-code')
		assert_that(link, is_not(none()))
			
		try:
			result = self.ds.execute_user_search('bankai')
			assert_that(result, has_entry('Items', has_length(greater_than(0))))
			fl = result['Items'][0]
			assert_that(fl.isDynamic, is_(True))
		finally:	
			self.ds.set_credentials(self.owner)
			self.ds.delete_object(friendsList)
			
	def test_dfl_links(self):
		self.ds.set_credentials(self.owner)
		friend_names = [r[0] for r in self.friends]
		suffix = str(uuid.uuid4()).split('-')[-1]
		flname = "sebonsakura-%s" % suffix
		friendsList = self.create_friends_list_with_name_and_friends(flname, friend_names, flname, locked=True)
		# make sure we don't have a link to get the code when the DFL is locked
		link = friendsList.get_link('default-trivial-invitation-code')
		assert_that(link, is_(none()))

if __name__ == '__main__':
	unittest.main()
