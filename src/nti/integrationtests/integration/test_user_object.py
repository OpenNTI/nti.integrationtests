import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import get_notification_count

from hamcrest import (assert_that, has_property,is_, is_not)

class TestUserObject(DataServerTestCase):

	user_one = ('test.user.6@nextthought.com', DataServerTestCase.default_user_password)
	user_two = ('test.user.7@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestUserObject, self).setUp()
		self.ds.set_credentials(self.user_one)
		self.container = 'test.user.container.%s' % time.time()

	def test_create_user(self):
		code =  str(uuid.uuid4()).split('-')[0]
		username = u'u' + code
		email = username + '@nextthought.com'
		password = 'mypassword'
		realname = 'real ' + code
		opt_in_email_communication = True
		user_object = self.ds.create_user(username, password, email, realname, opt_in_email_communication)
		assert_that(user_object, is_not(None))
		assert_that(user_object.email, is_(email))
		assert_that(user_object.name, is_(username))
		assert_that(user_object.realname, is_(realname))
		assert_that(user_object.opt_in_email_communication, is_(opt_in_email_communication))
		
	def test_notification_count_can_reset_by_changing_lastLoginTime(self):
		user_object = self.ds.get_user_object()

		created_objects = []
		if get_notification_count(user_object) < 2:
			for _ in xrange(3):
				created_obj = self.ds.create_note('A note to share', self.container, credentials=self.user_two)
				self.ds.share_object(created_obj, self.user_one[0], credentials=self.user_two)
				created_objects.append(created_obj)

		llt = user_object['lastLoginTime'] = time.time() + 5000
		del user_object._data['NotificationCount'] # Because now the NC we send is respected, so don't send one
		user_object = self.ds.update_object(user_object)
		assert_that( user_object, has_property( 'lastLoginTime', llt ) )
		assert_that( user_object, has_property( 'notificationCount', 0 ) )

		for created_object in created_objects:
			self.ds.delete_object(created_object, credentials=self.user_two)

if __name__ == '__main__':
	unittest.main()
