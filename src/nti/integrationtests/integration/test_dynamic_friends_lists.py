import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import container
from nti.integrationtests.integration import sortchanges
from nti.integrationtests.integration import shared_with
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import containing_friends
from nti.integrationtests.integration import container_of_length
from nti.integrationtests.integration import objects_from_container

from nti.integrationtests.integration import test_friends_lists
from nti.integrationtests.integration import test_friends_sharing

from hamcrest import (assert_that, is_, is_not, has_entry, greater_than_or_equal_to)

class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists,
							  test_friends_sharing.TestFriendsSharing):
	
	outsider = ('test.user.8@nextthought.com', DataServerTestCase.default_user_password)
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()		
		self.realname ='%s@nt.com' % str(uuid.uuid4()).split('-')[-1]
		
	def create_friends_list_with_name_and_friends(self, name, friends):
		dfl = self.ds.create_DFL_with_name_and_friends(name, friends, realname=self.realname)
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
			
	def test_dfl_search_t846(self):
		self.ds.set_credentials(self.owner)
		friend_names = [r[0] for r in self.friends]
		friendsList= self.create_friends_list_with_name_and_friends(self.list_name, friend_names)

		created_obj = self.ds.create_note(u'Zanjutsu Gokui', container=self.container, sharedWith=[friend_names[0]])

		try:
			self.ds.set_credentials(self.friends[0])
			content = self.ds.search_user_content("Zanjutsu")
			assert_that(content, has_entry('Hit Count', greater_than_or_equal_to(1)))
			
			# change shared w/ group
			self.ds.set_credentials(self.owner)
			created_obj.shareWith([self.list_name], reset=True)
			created_obj = self.ds.update_object(created_obj)
			assert_that(created_obj, shared_with([friendsList.ntiid]))
		
			# make sure the event is in the stream
			self.ds.set_credentials(self.friends[0])
			stream = self.ds.get_recursive_stream_data(self.container)
			assert_that(stream, is_(container()))
			sortedchanges = sortchanges(objects_from_container(stream))
							
			for c in sortedchanges:
				if c.changeType == 'Shared':
					assert_that(c.item, shared_with([friendsList.ntiid]))
					break							
		
			# do search
			content = self.ds.search_user_content("Gokui")
			assert_that(content, has_entry('Hit Count', greater_than_or_equal_to(1)))
		finally:	
			self.ds.set_credentials(self.owner)
			self.ds.delete_object(created_obj)
			self.ds.delete_object(friendsList)

if __name__ == '__main__':
	unittest.main()
