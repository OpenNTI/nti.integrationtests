import uuid
import unittest
	
from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.integration import shared_with
from nti.integrationtests.contenttypes import FriendsList
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import containing_friends
from nti.integrationtests.integration import container_of_length

from hamcrest import ( assert_that, is_, has_entry, greater_than_or_equal_to)

class TestFriendsSharing(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	friends = [('test.user.%s@nextthought.com' % r, DataServerTestCase.default_user_password) for r in xrange(2,4)]
	note = 'A note to share'
	
	def setUp(self):
		super(TestFriendsSharing, self).setUp()		
		self.ds.set_credentials(self.owner)
		self.list_name = '%s' % uuid.uuid1()
		self.container = generate_ntiid(nttype='friends')

	def create_friends_list_with_name_and_friends(self, name, friends):
		fl = FriendsList(name=name, friends=friends)
		return self.ds.create_friends_list(fl)

	def _create_friends_fake_notes(self):
		objects =[]
		for f in self.friends:
			username = f[0]
			container = str(uuid.uuid1())
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			note = self.ds.create_note('Fake note owned by %s' % username, container=container)
			objects.append(note)
		return objects

	def _delete_friends_fake_notes(self, objects):
		it = iter(objects)
		for f in self.friends:
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			self.ds.delete_object(it.next())

	def _check_object_in_friends(self, created_obj, container, friends):
		for f in friends:
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			user_data = self.ds.get_user_generated_data(container)
			assert_that(created_obj, contained_in(user_data))

	def test_share_with_friends(self):

		objects = self._create_friends_fake_notes()

		# restore credentials
		self.ds.set_credentials(self.owner)

		# create friends list
		friends = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(self.list_name, friends)
		self.assertTrue(friendsList is not None)

		# create an object to share
		created_obj = self.ds.create_note(self.note, container=self.container)
		self.assertTrue(created_obj is not None)

		# do the actual sharing
		created_obj.shareWith( self.list_name )
		shared_obj = self.ds.update_object(created_obj)
		self.assertTrue(shared_obj is not None)

		assert_that(shared_obj.id, is_(created_obj.id))
		
		# check that the friends can now see it
		self._check_object_in_friends(created_obj, self.container, self.friends)

		# clean up
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)
		self.ds.delete_object(created_obj)

		self._delete_friends_fake_notes(objects)

	def test_share_with_friends_and_remove_friend(self):
		objects = self._create_friends_fake_notes()
		self.ds.set_credentials(self.owner)

		# create friends list
		friends = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		# create and share
		created_obj = self.ds.create_note(self.note, container=self.container, sharedWith=friends)
		assert_that(created_obj, shared_with(friends))

		# check that the friends can now see it
		self._check_object_in_friends(created_obj, self.container, self.friends)
		self.ds.set_credentials(self.owner)

		# update friend list
		friends.pop()
		friendsList.friends = friends
		friendsList = self.ds.update_object(friendsList)
		assert_that(containing_friends(friendsList, friends))

		# check still I shared still can see the object
		self._check_object_in_friends(created_obj, self.container, self.friends)

		# clean up
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)
		self.ds.delete_object(created_obj)

		self._delete_friends_fake_notes(objects)

	def test_share_with_friends_and_delete_obj(self):

		objects = self._create_friends_fake_notes()
		self.ds.set_credentials(self.owner)

		# create friends list
		friends = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(self.list_name, friends)

		# create and share
		created_obj = self.ds.create_note(self.note, container=self.container, sharedWith=friends)
		assert_that(created_obj, shared_with(friends))

		# check that the friends can now see it
		self._check_object_in_friends(created_obj, self.container, self.friends)
		self.ds.set_credentials(self.owner)

		# remove object
		self.ds.delete_object(created_obj)

		for f in self.friends:
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			user_data = self.ds.get_user_generated_data(self.container)
			assert_that(user_data, container_of_length(0))

		# clean up
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)

		self._delete_friends_fake_notes(objects)
		
	def test_share_with_friends_and_search(self):

		self.ds.set_credentials(self.owner)
		
		list_name = self.list_name
		friendNames = [r[0] for r in self.friends]
		friendsList = self.create_friends_list_with_name_and_friends(list_name, friendNames)
		
		note = self.ds.create_note(u'Shibari Benihime', container=str(uuid.uuid4()), sharedWith=[list_name])
			
		for c in self.friends:
			self.ds.set_credentials(c)
			content = self.ds.search_user_content("Benihime")
			assert_that(content, has_entry('Hit Count', greater_than_or_equal_to(1)))
			
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(friendsList)
		self.ds.delete_object(note)

if __name__ == '__main__':
	unittest.main()
