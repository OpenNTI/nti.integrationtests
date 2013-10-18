#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time
import unittest

from nti.integrationtests.utils import phrases
from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains

from hamcrest import (is_, is_not, assert_that, has_length)

from nose.plugins.attrib import attr

@attr(level=3)
class TestBasicReplying(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicReplying, self).setUp()
		self.ds.set_credentials(self.owner)
		self.container = 'test.user.container.%s' % time.time()

	def test_create_basic_reply(self):
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)
		assert_that(created_reply['body'][0]), is_("A reply to note")
		assert_that(created_reply['inReplyTo'], is_(created_obj['id']))
		assert_that(created_reply['references'], is_([]))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)

	def test_share_basic_reply(self):
		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

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

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

		self.ds.unshare_object(created_reply, self.target[0], adapt=True)

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

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

		self.ds.unshare_object(created_obj, self.target[0], adapt=True)

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

		# check that the user can no longer see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, is_not(contains(created_reply)))

		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, is_not(contains(created_reply)))

		# cleanup
		self.ds.delete_object(created_obj)

	def test_replying_to_own_reply(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

		created_ps_reply = self.ds.create_note("PS. A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_ps_reply, self.target[0], adapt=True)

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

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

		created_response_reply = self.ds.create_note("A reply to a reply", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_response_reply, self.owner[0], adapt=True)

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

		# creates a reply to the note
		created_reply = self.ds.create_note("A reply to note", self.container, inReplyTo=created_obj['id'], adapt=True)

		self.ds.share_object(created_reply, self.target[0], adapt=True)

		try:
			# delete the test
			self.ds.delete_object(created_reply, credentials=self.target)
		except Exception:
			pass

		# check that the user can now see it
		ugd = self.ds.get_user_generated_data(self.container, credentials=self.owner, adapt=True)
		assert_that(ugd, contains(created_reply))

		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, contains(created_reply))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_reply)

	def test_multiple_replies(self):
		notes = []
		for x, txt in enumerate(phrases):
			txt = unicode(txt)
			if x == 0:
				note = self.ds.create_note(txt, self.container, adapt=True)
			else:
				note = self.ds.create_note(txt, self.container, inReplyTo=notes[0].id, adapt=True)
			notes.append(note)

		replies = self.ds.replies(notes[0])
		items = replies['Items']
		assert_that(items, has_length(len(phrases)-1))

if __name__ == '__main__':
	unittest.main()
