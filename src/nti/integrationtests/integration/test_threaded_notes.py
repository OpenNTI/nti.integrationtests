#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import time

from nti.integrationtests import DataServerTestCase

from nti.integrationtests.integration import not_shared
from nti.integrationtests.integration import only_shared_with

from nose.plugins.attrib import attr
from hamcrest import (assert_that, is_)

@attr(level=3)
class TestThreadedNotes(DataServerTestCase):

	user_one = ('test.user.1', 'temp001')
	user_two = ('test.user.2', 'temp001')
	user_three = ('test.user.3', 'temp001')

	def setUp(self):
		super(TestThreadedNotes, self).setUp()

		self.ds.set_credentials(self.user_one)		
		self.container = 'test_threaded_note-container-%s' % time.time()

	# FIXME to much knowledge required to do this
	def _replyToNote(self, text, container, inReplyTo, credentials=None):
		return self.ds.create_note(	text, container, credentials=credentials, \
									inReplyTo=inReplyTo.id, references=[inReplyTo.id])

	def test_not_shared_reply_to(self):
		note_to_reply_to = self.ds.create_note("A note to reply to", self.container)
		reply = self._replyToNote('The reply', self.container, note_to_reply_to)
		assert_that(reply, is_(not_shared()))

	def test_shared_reply_to(self):

		shareWith = [self.user_two[0], self.user_three[0]]

		note_to_reply_to = self.ds.create_note("A note to reply to", self.container)
		self.ds.share_object(note_to_reply_to, shareWith)

		reply = self._replyToNote('The reply', self.container, note_to_reply_to)
		assert_that(reply, is_(only_shared_with(shareWith)))

	def test_shared_reply_to_other(self):
		shareWith = [self.user_two[0], self.user_three[0]]

		note_to_reply_to = self.ds.create_note("A note to reply to", self.container)
		self.ds.share_object(note_to_reply_to, shareWith)

		reply = self._replyToNote('The reply', self.container, note_to_reply_to, credentials=self.user_two)

		#Should be shared with user_one (owner of original note) and user three
		assert_that(reply, is_(only_shared_with([self.user_one[0], self.user_three[0]])))


if __name__ == '__main__':
	import unittest
	unittest.main()
