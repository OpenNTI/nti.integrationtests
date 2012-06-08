import time
import unittest
	
from nti.integrationtests import DataServerTestCase

from nti.integrationtests.chat import generate_message

from nti.integrationtests.integration import contains
from nti.integrationtests.integration import contained_in
from nti.integrationtests.integration import object_from_container
from nti.integrationtests.integration import container_of_length

from hamcrest import is_
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than_or_equal_to

class TestBasicUserGeneratedData(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicUserGeneratedData, self).setUp()
		
		self.container = 'test_basic_ugd-container-%s' % time.time()
		self.ds.set_credentials(self.owner)

		# we clean these up in different places for each test
		self.created_note = self.ds.create_note("A note to test with", self.container)
		self.created_highlight = self.ds.create_highlight('but', self.container,)

	def test_created_objects_show_in_ugd(self):
		
		ugd = self.ds.get_user_generated_data(self.container)

		assert_that(ugd, is_(container_of_length(2)))
		assert_that(ugd, contains(self.created_note))
		assert_that(ugd, contains(self.created_highlight))

		# cleanup
		self.ds.delete_object(self.created_note)
		self.ds.delete_object(self.created_highlight)

	def test_delete_removes_from_ugd(self):
		
		ugd = self.ds.get_user_generated_data(self.container)

		assert_that(ugd, is_(container_of_length(2)))
		assert_that(ugd, contains(self.created_note))
		assert_that(ugd, contains(self.created_highlight))

		# cleanup
		self.ds.delete_object(self.created_note)
		self.ds.delete_object(self.created_highlight)

		ugd = self.ds.get_user_generated_data(self.container)
		assert_that(ugd, is_(container_of_length(0)))
		assert_that(self.created_note, is_not(contained_in(ugd)))
		assert_that(self.created_highlight, is_not(contained_in(ugd)))

	def test_update_reflects_in_ugd(self):
		
		ugd = self.ds.get_user_generated_data(self.container)

		assert_that(ugd, is_(container_of_length(2)))
		assert_that(ugd, contains(self.created_note))
		assert_that(ugd, contains(self.created_highlight))

		self.created_highlight['startHighlightedText'] = 'new'
		updated_highlight = self.ds.update_object(self.created_highlight)

		ugd = self.ds.get_user_generated_data(self.container)

		assert_that(ugd, is_(container_of_length(2)))
		assert_that(ugd, contains(self.created_note))
		assert_that(ugd, contains(self.created_highlight))

		ugdHighlight = object_from_container(ugd, updated_highlight)
		assert_that(ugdHighlight, has_entry('startHighlightedText', 'new'))

		# cleanup
		self.ds.delete_object(self.created_note)
		self.ds.delete_object(self.created_highlight)
		
	def test_created_75_show_in_ugd(self):
		for _ in xrange(75):
			message = generate_message(k=3)
			self.created_note = self.ds.create_note(message, self.container)
		
		ugd = self.ds.get_user_generated_data(self.container)
		items = ugd['Items']
		assert_that(items, has_length(greater_than_or_equal_to(75)))

if __name__ == '__main__':
	unittest.main()
