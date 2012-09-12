import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.utils import generate_ntiid
from nti.integrationtests.utils import generate_random_text
from nti.integrationtests.contenttypes.users import DynamicFriendsList

from hamcrest import (is_not, assert_that)

class TestDynamicFriendsLists(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	unauthorized_target = ('test.user.3@nextthought.com', 'incorrect')
	noteToCreateAndShare = {'text': 'A note to share'}
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()
		self.container = generate_ntiid(date=time.time(), nttype=generate_random_text())
		self.ds.set_credentials(self.owner)


	def xtest_create_dfl(self):
		name = generate_random_text() + '-' + str(time.time())
		dfl = DynamicFriendsList(name=name, creator=self.owner[0], ntiid=self.container, friends=[self.target[0]])
		dfl = self.ds.create_friends_list(dfl)
		assert_that(dfl, is_not(None))

if __name__ == '__main__':
	unittest.main()
