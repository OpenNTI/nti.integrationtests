import time
import unittest
	
from servertests import DataServerTestCase
from servertests.integration import contains

from hamcrest import assert_that
from hamcrest import is_not
from hamcrest import is_

class TestBasicReplying(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicReplying, self).setUp()
		
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)

	def test_create_basic_reply(self):
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		assert_that(created_reply['body'][0]), is_("A reply to note")
		assert_that(created_reply['inReplyTo'], is_(created_obj['id']))
		assert_that(created_reply['references'], is_(None))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
	
	def test_share_basic_reply(self):
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_reply))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
		
	def test_revoke_basic_reply(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)
		
		self.ds.unshare_object(created_reply, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(created_reply['sharedWith'], is_not(self.target[0]))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
	
	def test_revoke_note_with_reply(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)
		
		self.ds.unshare_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(created_reply['sharedWith'], is_not(self.target[0]))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
		
	def test_delete_shared_reply(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)

		# delete the test
		self.ds.delete_object(created_reply)
		
		self.ds.wait_for_event()
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, is_not(contains(created_reply)))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		# cleanup
		self.ds.delete_object(created_obj)
		
	def test_replying_to_own_reply(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)
		
		created_ps_reply = self.ds.create_note("PS. A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_ps_reply, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_ps_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_ps_reply))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
		self.ds.delete_object(created_ps_reply)
		
	def test_replying_to_other_reply(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)
		
		created_response_reply = self.ds.create_note("A reply to a reply", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_response_reply, self.owner[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_response_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_response_reply))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
		self.ds.delete_object(created_response_reply)
		
	def test_delete_basic_reply_by_other_user(self):
		
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)
		
		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)
		
		self.ds.wait_for_event()
		
		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		
		self.ds.share_object(created_reply, self.target[0], adapt=True)

		try:
			# delete the test
			self.ds.delete_object(created_reply, credentials=self.target)
		except AssertionError:
			pass
		
		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_reply))
		
		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)
		
if __name__ == '__main__':
	unittest.main()