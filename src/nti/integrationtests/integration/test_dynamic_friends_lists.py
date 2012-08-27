import time
import random
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.contenttypes.users import DynamicFriendsList

#from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that

class TestDynamicFriendsLists(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	target = ('test.user.2@nextthought.com', DataServerTestCase.default_user_password)

	unauthorized_target = ('test.user.3@nextthought.com', 'incorrect')
	noteToCreateAndShare = {'text': 'A note to share'}

	@classmethod
	def generate_random_text(cls, a_max=5):
		word = []
		for _ in xrange(a_max+1):
			word.append(chr(random.randint(ord('a'), ord('z'))))
		return "".join(word)
	
	def setUp(self):
		super(TestDynamicFriendsLists, self).setUp()
		self.container = generate_ntiid(date=time.time(), nttype=self.generate_random_text())
		self.ds.set_credentials(self.owner)


	def xtest_create_dfl(self):
		name = self.generate_random_text() + '-' + str(time.time())
		dfl = DynamicFriendsList(name=name, creator=self.owner[0], ntiid=self.container, friends=[self.target[0]])
		dfl = self.ds.create_friends_list(dfl)
		assert_that(dfl, is_not(None))

if __name__ == '__main__':
	unittest.main()
