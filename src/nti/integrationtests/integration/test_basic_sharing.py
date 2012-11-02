import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains
from nti.integrationtests.integration import shared_with
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import has_same_oid_as
from nti.integrationtests.integration import container_of_length_greater_than_or_equal_to

from hamcrest import (is_, assert_that, is_not)

class TestBasicSharing(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)
	user_3 = ('test.user.3@nextthought.com', DataServerTestCase.default_user_password)
	
	unauthorized_target = ('test.user.3@nextthought.com', 'incorrect')
	noteToCreateAndShare = {'text': 'A note to share'}

	def setUp(self):
		super(TestBasicSharing, self).setUp()

		self.container = 'test_basic_sharing-container-%s' % time.time()
		self.ds.set_credentials(self.owner)

	def test_basic_sharing(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0], adapt=True)
		assert_that(shared_obj, has_same_oid_as(created_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		self.ds.wait_for_event()

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(ugd, contains(shared_obj))

		# cleanup
		self.ds.delete_object(created_obj)

	def test_basic_sharing_incorrect_data(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		other_obj =  self.ds.create_note('A note not to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0], adapt=True)
		assert_that(shared_obj, has_same_oid_as(created_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		self.ds.wait_for_event()

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(ugd, is_not(contains(other_obj)))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(other_obj)

	def test_sharing_multiple_data(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		other_obj =  self.ds.create_note('A note not to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0], adapt=True)
		assert_that(shared_obj, has_same_oid_as(created_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		shared_obj = self.ds.share_object(other_obj, self.target[0], adapt=True)
		assert_that(shared_obj, has_same_oid_as(other_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		self.ds.wait_for_event()

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		__traceback_info__ = ugd, created_obj, other_obj, shared_obj
		assert_that(ugd, contains(other_obj))
		assert_that(ugd, contains(created_obj))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(other_obj)

	def get_object(self, link, credentials):
		try:
			return self.ds.get_object(link=link, credentials=credentials)
		except:
			return None
		
	def test_revoke_sharing(self):

		# create the object to share
		self.ds.set_credentials(self.owner)
		created_obj = self.ds.create_note('A note to share', self.container)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0])
		assert_that(shared_obj, has_same_oid_as(created_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target)
		assert_that(ugd, contains(shared_obj))

		link = shared_obj.get_edit_link()
		assert_that(self.get_object(link=link, credentials=self.target), is_not(None))
		assert_that(self.get_object(link=link, credentials=self.user_3), is_(None))
		
		# unshare it
		unshared_obj = self.ds.unshare_object(shared_obj, self.target[0])
		assert_that(unshared_obj, has_same_oid_as(created_obj))
		assert_that(unshared_obj, is_not(shared_with(self.target[0])))

		# check that the user can now see it
		container = self.ds.get_user_generated_data(self.container, credentials=self.target)
		assert_that(created_obj, is_not(contained_in(container)))
			
		try:
			link = unshared_obj.get_edit_link()
			obj = self.get_object(link=link, credentials=self.target)
			if obj is not None:
				self.fail("user can still access unshared object")
		finally:
			self.ds.delete_object(created_obj)

	def test_revoke_selected_share(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		other_obj =  self.ds.create_note('A note not to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj1 = self.ds.share_object(created_obj, self.target[0], adapt=True)
		assert_that(shared_obj1, has_same_oid_as(created_obj))
		assert_that(shared_obj1, shared_with(self.target[0]))

		shared_obj2 = self.ds.share_object(other_obj, self.target[0], adapt=True)
		assert_that(shared_obj2, has_same_oid_as(other_obj))
		assert_that(shared_obj2, shared_with(self.target[0]))

		unshared_obj = self.ds.unshare_object(shared_obj1, self.target[0])
		assert_that(unshared_obj, has_same_oid_as(created_obj))
		assert_that(unshared_obj, is_not(shared_with(self.target[0])))

		self.ds.wait_for_event()

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(ugd, contains(other_obj))
		assert_that(ugd, is_not(contains(created_obj)))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(other_obj)

	def test_share_not_found(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# delete note
		self.ds.delete_object(created_obj)

		# do the actual sharing
		try:
			self.ds.share_object(created_obj, self.target[0], adapt=True)
		except AssertionError:
			pass
		else:
			self.fail("Expected 404 exception")

		# Now it should no longer exist
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(ugd, is_not(contains(created_obj)))

	def test_unauthorized_sharing(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		shared_obj = None

		try:
			shared_obj = self.ds.share_object(created_obj, self.unauthorized_target[0], credentials=self.unauthorized_target, adapt=True)
		except Exception:
			pass

		# check that the user can not see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(shared_obj, is_(None))
		assert_that(ugd, is_not(contains(created_obj)))

		# cleanup
		self.ds.delete_object(created_obj)

	def test_deleting_shared_note_removes_from_target(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0], adapt=True)

		#removes the object after sharing
		self.ds.delete_object(created_obj)

		self.ds.wait_for_event()

		#creates the variable ugd
		ugd = None
		try:
			ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		except Exception:
			pass

		#asserts that the shared object contains none.
		assert_that(ugd, is_not(contains(shared_obj)))

	def test_create_and_share_note(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, sharedWith=[self.owner[0], self.target[0]], adapt=True)

		self.ds.wait_for_event()

		assert_that(created_obj['body'][0], is_('A note to share'))
		assert_that(created_obj['sharedWith'], is_([self.target[0]]))

		# cleanup
		self.ds.delete_object(created_obj)

	def test_share_note_through_dict(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, sharedWith=[self.owner[0], self.target[0]], adapt=True)

		self.ds.wait_for_event()

		shared_obj = self.ds.share_object(created_obj, [self.owner[0], self.target[0]])
		assert_that(shared_obj['sharedWith'], is_(['test.user.2@nextthought.com']))

	def test_search_direct_shared(self):
		msg = 'Aizen using Hado #90: Kurohitsugi (Black Coffin).'
		
		self.ds.set_credentials(self.owner)
		note = self.ds.create_note(msg, self.container, adapt=True)
		note = self.ds.share_object(note, self.target[0], adapt=True)

		to_search = 'Kurohitsugi'
		self.ds.set_credentials(self.target)
		result = self.ds.unified_search(to_search, self.container)
		assert_that(result, container_of_length_greater_than_or_equal_to(1))

		self.ds.set_credentials(self.owner)
		self.ds.delete_object(note)
		
		self.ds.set_credentials(self.target)
		result = self.ds.unified_search(to_search, self.container)
		assert_that(result, container_of_length_greater_than_or_equal_to(0))
		
	def test_search_friend_list_shared(self):

		uid = str(uuid.uuid4()).split('-')[0]
		list_name = '%s-%s@nextthought.com' % (uid, time.time())
		friends = ['test.user.2@nextthought.com', 'test.user.3@nextthought.com']
		createdlist = self.ds.create_friends_list_with_name_and_friends(list_name, friends)

		msg = 'Suzumebachi Hisagomaru'
		self.ds.set_credentials(self.owner)
		note = self.ds.create_note(msg, self.container, adapt=True)
		note = self.ds.share_object(note, [list_name], adapt=True)
		
		to_search = 'Hisagomaru'
		self.ds.set_credentials(self.user_3)
		result = self.ds.unified_search(to_search, self.container)
		assert_that(result, container_of_length_greater_than_or_equal_to(1))
		
		self.ds.set_credentials(self.owner)
		self.ds.delete_object(note)
		self.ds.delete_object(createdlist)

if __name__ == '__main__':
	unittest.main()
