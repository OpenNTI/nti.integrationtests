import uuid

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.integration import container
from nti.integrationtests.integration import container_of_length

from hamcrest import assert_that

class TestUserSearch(DataServerTestCase):

	def setUp(self):
		super(TestUserSearch, self).setUp()
		self.prefix = 'test.user'
		self.container = 'container-%s' % uuid.uuid1()
		self.users = [('%s.%s@nextthought.com' % (self.prefix, r), self.default_user_password) for r in range(15,19)]

	def test_search_users(self):

		self.ds.set_credentials(self.users[0])

		result = self.ds.execute_user_search(self.prefix)
		assert_that(result, container())
		self.assertGreaterEqual(len(result['Items']), 100)

		result = self.ds.execute_user_search("%s.15" % self.prefix)
		assert_that(result, container_of_length(1))

		# not a reg exp
		result = self.ds.execute_user_search("%s.2*" % self.prefix)
		assert_that(result, container_of_length(0))

		result = self.ds.execute_user_search("this_user_dne")
		assert_that(result, container_of_length(0))

if __name__ == '__main__':
	import unittest
	unittest.main()
