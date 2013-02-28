import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import contains

from nose.tools import assert_raises
from hamcrest import (assert_that, is_, not_none, greater_than_or_equal_to, none)

class TestBlogging(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestBlogging, self).setUp()
		self.ds.set_credentials(self.owner)

	def test_create_post(self):
		post = self.ds.create_blog_post('Shikai vs Bankai', 'No Zanpakuto in existence has a Shikai and a Bankai that use unrelated abilities')
		assert_that(post, not_none())
		assert_that(post.description, is_('Shikai vs Bankai'))
		
		blog = self.ds.get_blog()
		assert_that(blog.topicCount, greater_than_or_equal_to(1))
		
		contents = self.ds.get_blog_contents()
		assert_that(contents, contains(post))

	def test_user_cannot_change_sharing_on_blog_entry(self):
		post = self.ds.create_blog_post('Bankai Ability', 'A mere upgrade?')
		assert_that(post, not_none())
		
		ps = post.headline
		ps.body=['A 10 time upgrade']
		ps.sharedWith = [self.target[0]]
		ps = self.ds.update_object(ps)
		
		assert_that(ps.body, is_(['A 10 time upgrade']))
		assert_that(ps.sharedWith, is_([]))
		
		post = self.ds.create_blog_post('Ichigo', 'A fake Shinigami?', sharedWith=[self.target[0]])
		assert_that(post, not_none())
		assert_that(post.sharedWith, is_([]))
		
	def test_delete_post_with_edit_link(self):
		post = self.ds.create_blog_post('Spain', 'A no ending nightmare')
		assert_that(post, not_none())
		
		ps = post.headline
		ps.body=['Uncertain Future']
		ps = self.ds.update_object(ps)
		
		with assert_raises(Exception):
			self.ds.delete_object(ps)

	def test_publish_unpublish(self):
		post = self.ds.create_blog_post("Kurosaki Ichigo", 'What is he human? Shinigami? Quincy?')
		assert_that(post, not_none())
		
		published_post = self.ds.publish_post(post)
		assert_that(published_post, is_(not_none()))
		
		unpublish = published_post.get_unpublish_link()
		assert_that(unpublish, is_(not_none()))
		assert_that(published_post.get_publish_link(), is_(none()) )
		
		unpublish_object = self.ds.unpublish_post(published_post)
		assert_that(unpublish_object, is_(not_none()))
		assert_that(unpublish_object.get_unpublish_link(), is_(none()) )

if __name__ == '__main__':
	unittest.main()
