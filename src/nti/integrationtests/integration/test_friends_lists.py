import time

from nti.integrationtests import DataServerTestCase

from nti.integrationtests.integration import containing_friend
from nti.integrationtests.integration import containing_friends
from nti.integrationtests.integration import containing_no_friends
from nti.integrationtests.integration import contains_friendslist
from nti.integrationtests.integration import friends_list_from_friends_lists
from nti.integrationtests.integration import accepting

from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_key


class TestBasicFriendsLists(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	friend = ('test.user.3@nextthought.com',DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicFriendsLists, self).setUp()
		
		self.ds.set_credentials(self.owner)		
		self.list_name = 'test_friend_list-%s@nextthought.com' % time.time()

	#TODO: add test resolved vs. unresolved

	def test_has_everyone_by_default(self):
		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist('Everyone'))

	def test_can_create_empty_friendslist(self):
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, [])
		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_no_friends(friendsList))

		self.ds.delete_object(createdlist)

	def test_can_delete_friendslist(self):

		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, friends)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))

		self.ds.delete_object(createdlist)
		lists = self.ds.get_friends_lists()
		assert_that(lists, is_not(contains_friendslist(self.list_name)))
		
	def test_can_create_friendslist_with_friends(self):
		
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, friends)

		lists = self.ds.get_friends_lists()
		assert_that(lists, contains_friendslist(self.list_name))

		friendsList = friends_list_from_friends_lists(lists, self.list_name)
		assert_that(containing_friends(friendsList, friends))
		
		self.ds.delete_object(createdlist)

	def test_can_delete_from_friendslist(self):
		
		friends = ['test.user.5@nextthought.com', 'test.user.6@nextthought.com']
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, friends)

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
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, [])

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
		"""
		When a user is circled they are automatically accepting the user that circled them
		"""
		createdlist = self.ds.create_friends_list_with_name_and_friends(self.list_name, [self.friend[0]])

		self.ds.wait_for_event()

		friends_user_object = self.ds.get_user_object(credentials=self.friend)
		assert_that(accepting(friends_user_object, self.owner[0]))

		self.ds.delete_object(createdlist)

if __name__ == '__main__':
	import unittest
	unittest.main()
