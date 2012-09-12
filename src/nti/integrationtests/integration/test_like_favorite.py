import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_message

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import greater_than

class TestLikeFavorite(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestLikeFavorite, self).setUp()
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)

	def test_like_unlike_note(self):
		msg = generate_message(k=3)
		created_obj = self.ds.create_note(msg, self.container, adapt=True)
		assert_that(created_obj.get_like_link(), is_not(None) )
		
		liked_object = self.ds.like_object(created_obj)
		assert_that(liked_object, is_not(None))
		assert_that(liked_object.likeCount, is_(1))
		
		unlike = liked_object.get_unlike_link()
		assert_that(unlike, is_not(None))
		assert_that(liked_object.get_like_link(), is_(None) )
		
		unliked_object = self.ds.unlike_object(liked_object)
		assert_that(unliked_object, is_not(None))
		assert_that(unliked_object.get_unlike_link(), is_(None) )
		assert_that(unliked_object.likeCount, is_(0))
		
	def test_fav_unfav_note(self):
		msg = generate_message(k=3)
		created_obj = self.ds.create_note(msg, self.container, adapt=True)
		assert_that(created_obj.get_favorite_link(), is_not(None) )
		
		faved_object = self.ds.fav_object(created_obj)
		assert_that(faved_object, is_not(None))
		
		unfav = faved_object.get_unfavorite_link()
		assert_that(unfav, is_not(None))
		assert_that(faved_object.get_favorite_link(), is_(None) )
		
		unfav_object = self.ds.unfav_object(faved_object)
		assert_that(unfav_object, is_not(None))
		assert_that(unfav_object.get_unfavorite_link(), is_(None) )
		
	def test_like_moddate(self):
		msg = generate_message(k=3)
		created_obj = self.ds.create_note(msg, self.container, adapt=True)
		lm = created_obj.lastModified
		
		time.sleep(2)
		
		liked_object = self.ds.like_object(created_obj)
		assert_that(liked_object, is_not(None))
		
		lm2 = liked_object.lastModified
		assert_that(lm2, greater_than(lm))
		
if __name__ == '__main__':
	unittest.main()