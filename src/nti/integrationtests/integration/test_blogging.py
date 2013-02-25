import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains

from hamcrest import (assert_that, is_, not_none, greater_than_or_equal_to, less_than)

class TestBasicStream(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBasicStream, self).setUp()
		self.ds.set_credentials(self.owner)

	def xtest_create_post(self):
		post = self.ds.create_blog_post('Shikai vs Bankai', 'No Zanpakuto in existence has a Shikai and a Bankai that use unrelated abilities')
		assert_that(post, not_none())
		assert_that(post.description, is_('Shikai vs Bankai'))
		
		blog = self.ds.get_blog()
		assert_that(blog.topicCount, greater_than_or_equal_to(1))
		
		contents = self.ds.get_blog_contents()
		assert_that(contents, contains(post))

	def xtest_user_cannot_change_sharing_on_blog_entry(self):
		post = self.ds.create_blog_post('Bankai Ability', 'A mere upgrade?')
		assert_that(post, not_none())
		
		ps = post.story
		ps.body=['A 10 time upgrade']
		ps.sharedWith = [self.target[0]]
		ps = self.ds.update_object(ps)
		
		assert_that(ps.body, is_(['A 10 time upgrade']))
		assert_that(ps.sharedWith, is_([]))
		
		post = self.ds.create_blog_post('Ichigo', 'A fake Shinigami?', sharedWith=[self.target[0]])
		assert_that(post, not_none())
		assert_that(post.sharedWith, is_([]))
		
	def test_create_edit_delete(self):
		blog = self.ds.get_blog()
		tc = blog.topicCount
		
		post = self.ds.create_blog_post('Spain', 'A no ending nightmare')
		assert_that(post, not_none())
		
		ps = post.story
		ps.body=['Uncertain Future']
		ps = self.ds.update_object(ps)
		
		self.ds.delete_object(ps)
		
		blog = self.ds.get_blog()
		assert_that(blog.topicCount, less_than(tc))

if __name__ == '__main__':
	unittest.main()
