import time
import unittest

from servertests import DataServerTestCase
from servertests.integration import contained_in
from servertests.integration import shared_with
from servertests.integration import has_same_oid_as
from servertests.integration import contains

from hamcrest import assert_that
from hamcrest import is_not
from hamcrest import is_

class TestBasicSharing(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

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

		assert_that(ugd, contains(other_obj))
		assert_that(ugd, contains(created_obj))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(other_obj)

	def test_revoke_sharing(self):
		
		# create the object to share
		created_obj = self.ds.create_note('A note to share', self.container)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0])
		assert_that(shared_obj, has_same_oid_as(created_obj))
		assert_that(shared_obj, shared_with(self.target[0]))

		self.ds.wait_for_event()

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target)
		assert_that(ugd, contains(shared_obj))

		# unshare it
		unshared_obj = self.ds.unshare_object(shared_obj, self.target[0])
		assert_that(unshared_obj, has_same_oid_as(created_obj))
		assert_that(unshared_obj, is_not(shared_with(self.target[0])))

		self.ds.wait_for_event()

		# check that the user can now see it
		container = self.ds.get_user_generated_data(self.container, credentials=self.target)
		assert_that(created_obj, is_not(contained_in(container)))

		# cleanup
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
		shared_obj1 = None

		# do the actual sharing
		try:
			shared_obj1 = self.ds.share_object(created_obj, self.target[0], adapt=True)
		except AssertionError: 
			pass

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)

		assert_that(shared_obj1, is_(None))
		assert_that(ugd, is_not(contains(created_obj)))

	def test_unauthorized_sharing(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		shared_obj = None
		
		try:
			shared_obj = self.ds.share_object(created_obj, self.unauthorized_target[0], credentials=self.unauthorized_target, adapt=True)
		except AssertionError:
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
		except AssertionError:
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

if __name__ == '__main__':
	unittest.main()
