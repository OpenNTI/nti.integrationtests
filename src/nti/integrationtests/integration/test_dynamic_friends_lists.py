import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import shared_with
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import containing_friends

from nti.integrationtests.integration import test_friends_lists
from nti.integrationtests.integration import test_friends_sharing

from hamcrest import ( assert_that, is_not)


class TestDynamicFriendsLists(test_friends_lists.TestBasicFriendsLists,
							  test_friends_sharing.TestFriendsSharing):
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()		
		self.realname ='%s@nt.com' % str(uuid.uuid4()).split('-')[-1]
		
	def create_friends_list_with_name_and_friends(self, name, friends):
		dfl = self.ds.create_DFL_with_name_and_friends(name, friends, realname=self.realname)
		return dfl
	
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
		
if __name__ == '__main__':
	unittest.main()
