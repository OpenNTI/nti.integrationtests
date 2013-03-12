#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.integration import container
from nti.integrationtests.integration import contains
from nti.integrationtests.integration import sortchanges
from nti.integrationtests.integration import wraps_item
from nti.integrationtests.integration import unwrap_object
from nti.integrationtests.integration import has_same_oid_as
from nti.integrationtests.integration import has_circled_event
from nti.integrationtests.integration import of_change_type_shared
from nti.integrationtests.integration import objects_from_container
from nti.integrationtests.integration import get_notification_count
from nti.integrationtests.integration import of_change_type_modified

from hamcrest import (assert_that, has_entry, is_, is_not, less_than_or_equal_to,
					  not_none, greater_than_or_equal_to, has_length)
does_not = is_not

from nose.plugins.attrib import attr

@attr(priority=3)
class TestBasicStream(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)
	three = ('test.user.3@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicStream, self).setUp()

		self.container = generate_ntiid(nttype='stream')
		self.ds.set_credentials(self.owner)

	def test_sharing_goes_to_stream(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0])
		assert_that(shared_obj, not_none())

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)
		assert_that(stream, is_(container()))

		sortedchanges = sortchanges(objects_from_container(stream))
		assert_that( sortedchanges, has_length( greater_than_or_equal_to( 1 ) ) )
		change = sortedchanges[0]
		assert_that(change, of_change_type_shared())
		assert_that(change, wraps_item(created_obj))

		created_obj2 = self.ds.create_note('A note to share 2', self.container)
		self.ds.share_object(created_obj2, self.target[0])

		created_obj3 =  self.ds.create_note('A note to share 3', self.container)
		self.ds.share_object(created_obj3, self.target[0])

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)
		assert_that(stream, is_(container()))

		sortedchanges = sortchanges(objects_from_container(stream))
		assert_that(sortedchanges[0], wraps_item(created_obj3))
		assert_that(sortedchanges[0], of_change_type_shared())

		assert_that(sortedchanges[1], wraps_item(created_obj2))
		assert_that(sortedchanges[1], of_change_type_shared())

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(created_obj2)
		self.ds.delete_object(created_obj3)

	def test_update_goes_to_stream(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share 3', self.container)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0])

		# FIXME: need to abstract this but it requires something more than a plain dict
		# now edit the object.
		updatedText = 'updated text'
		shared_obj['body'] = [updatedText]
		updatedObj = self.ds.update_object(shared_obj)

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)

		# we should have two things. The intial create and then the update	we have another
		# test to verify the create so we only explicitly check for the update
		assert_that( stream, is_(container()) )
		assert_that( stream, has_length( greater_than_or_equal_to( 2 ) ) )

		sortedchanges = sortchanges(objects_from_container(stream))
		assert_that( sortedchanges, has_length( greater_than_or_equal_to( 1 ) ) )
		update_change = sortedchanges[0]
		assert_that(update_change, of_change_type_modified())
		assert_that(update_change, wraps_item(updatedObj))
		assert_that(unwrap_object(update_change), has_entry('body', [updatedText]))

		# cleanup
		self.ds.delete_object(created_obj)

	def test_delete_doesnt_goes_to_stream(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share 3', self.container)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0])
		assert_that(shared_obj, not_none())

		# now delete it
		self.ds.delete_object(created_obj)

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)

		# things that are deleted don't show up in the stream at all.  Verify that
		assert_that(stream, is_(container()))

		sortedchanges = sortchanges(objects_from_container(stream))
		for change in sortedchanges:
			assert_that(change, does_not(wraps_item(created_obj)))

	def test_creating_friendslist_goes_to_stream(self):

		list_name = str(uuid.uuid4())
		createdlist = self.ds.create_friends_list_with_name_and_friends(list_name, [self.target[0]])

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.root_item, credentials=self.target)

		assert_that(stream, is_(container()))

		sortedchanges = sortchanges(objects_from_container(stream))
		__traceback_info__ = createdlist, stream
		assert_that( sortedchanges, has_length( greater_than_or_equal_to( 1 ) ) )
		assert_that( has_circled_event(sortedchanges))

		# cleanup
		self.ds.delete_object(createdlist)

	def test_adding_to_friendslist_goes_to_stream(self):

		list_name = str(uuid.uuid4())
		createdlist = self.ds.create_friends_list_with_name_and_friends(list_name, [])
		createdlist.friends = [self.target[0]]

		updatedlist = self.ds.update_object(createdlist)
		assert_that(updatedlist, not_none())

		# check that it is in the stream
		stream = self.ds.get_recursive_stream_data(self.root_item, credentials=self.target)

		# things that are deleted don't show up in the stream.  Verify that
		assert_that(stream, is_(container()))

		sortedchanges = sortchanges(objects_from_container(stream))
		assert_that( sortedchanges, has_length( greater_than_or_equal_to( 1 ) ) )

		assert_that( has_circled_event(sortedchanges))

		# cleanup
		self.ds.delete_object(createdlist)

	def test_stream_increments_user_notification_count(self):

		target_user_object = self.ds.get_user_object(credentials=self.target)
		starting_count = get_notification_count(target_user_object)

		created_obj =  self.ds.create_note('A note to share', self.container)
		self.ds.share_object(created_obj, self.target[0])

		target_user_object = self.ds.get_user_object(credentials=self.target)

		# Notice, however, that because of background processes still finishing,
		# the count may not be exact. It may be higher.
		target_notification_count = starting_count + 1
		user_not_count = target_user_object.notificationCount
		assert_that(user_not_count, greater_than_or_equal_to(target_notification_count))

		created_obj['body'] = ['junk']
		self.ds.update_object(created_obj)

		# we want to circle but we have already circled target so we get no notification
		list_name = str(uuid.uuid4())
		createdlist = self.ds.create_friends_list_with_name_and_friends(list_name, [self.target[0]], credentials=self.three)
		target_user_object = self.ds.get_user_object(credentials=self.target)
		target_notification_count = starting_count + 1
		user_not_count = target_user_object.notificationCount
		assert_that(user_not_count, greater_than_or_equal_to(target_notification_count))

		# cleanup
		self.ds.delete_object(created_obj)
		self.ds.delete_object(createdlist, credentials=self.three)

	def test_user_keeps_deleting_note(self):

		# create the object to share
		created_obj =  self.ds.create_note('A note to share', self.container, adapt=True)

		# do the actual sharing
		shared_obj = self.ds.share_object(created_obj, self.target[0], adapt=True)

		self.ds.delete_object(created_obj)

		ugd = self.ds.get_user_generated_data(self.container, credentials=self.target, adapt=True)
		assert_that(ugd, is_not(contains(shared_obj)))

	def test_bounded_server_stream(self):

		notes_array = []
		MAX_SHARES = 50
		MAX_SHARES_P1 = MAX_SHARES + 1
		NUMBER_OF_SHARES = 65

		notes = 0
		while notes < NUMBER_OF_SHARES:

			# create the object to share
			created_obj =  self.ds.create_note('Note number %s' % notes, self.container, adapt=True)

			#appends the newly created note to the array
			notes_array.append(created_obj)

			# do the actual sharing
			self.ds.share_object(created_obj, self.target[0], adapt=True)

			#increments the value of notes
			notes += 1

		initial_stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)
		initial_sortedchanges = sortchanges(objects_from_container(initial_stream))

		assert_that(initial_stream, is_(container()))
		initial_sortedchanges = [c for c in initial_sortedchanges if c.changeType != 'Circled']
		assert_that( initial_sortedchanges, has_length( less_than_or_equal_to( NUMBER_OF_SHARES ) ) )
		assert_that( initial_sortedchanges, has_length( less_than_or_equal_to( MAX_SHARES_P1 ) ) )

		# create the object to share
		created_obj =  self.ds.create_note('Note number %s' % notes, self.container, adapt=True)

		# appends the newly created note to the array
		notes_array.append(created_obj)

		# do the actual sharing
		self.ds.share_object(created_obj, self.target[0], adapt=True)

		final_stream = self.ds.get_recursive_stream_data(self.container, credentials=self.target)
		final_sortedchanges = sortchanges(objects_from_container(final_stream))

		assert_that(final_stream, is_(container()))
		final_sortedchanges = [c for c in final_sortedchanges if c.changeType != 'Circled']
		assert_that( final_sortedchanges, has_length( less_than_or_equal_to( NUMBER_OF_SHARES ) ) )
		assert_that( final_sortedchanges, has_length( less_than_or_equal_to( MAX_SHARES_P1 ) ) )

		assert_that(final_sortedchanges[1], has_same_oid_as( initial_sortedchanges[0] ) )

if __name__ == '__main__':
	unittest.main()
