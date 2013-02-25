import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains

from hamcrest import (assert_that, is_, not_none, greater_than_or_equal_to)

class TestBasicStream(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicStream, self).setUp()
		self.ds.set_credentials(self.owner)

	def test_create_post(self):
		post = self.ds.create_blog_post('Shikai vs Bankai', 'No Zanpakuto in existence has a Shikai and a Bankai that use unrelated abilities')
		assert_that(post, not_none())
		assert_that(post.description, is_('Shikai vs Bankai'))
		
		blog = self.ds.get_blog()
		assert_that(blog.topicCount, greater_than_or_equal_to(1))
		
		contents = self.ds.get_blog_contents()
		assert_that(contents, contains(post))

	@unittest.expectedFailure
	def test_share_post(self):
		post = self.ds.create_blog_post('Bankai Ability', 'A mere upgrade?')
		assert_that(post, not_none())
		
		ps = post.story
		ps.body=['A 10 time upgrade']
		ps.sharedWith = [self.target[0]]
		ps = self.ds.update_object(ps)
		
		assert_that(ps.body, is_(['A 10 time upgrade']))
		assert_that(ps.sharedWith, is_([self.target[0]]))
		
		contents = self.ds.get_blog_contents(credentials=self.target)
		assert_that(contents, contains(post))
		
if __name__ == '__main__':
	unittest.main()
