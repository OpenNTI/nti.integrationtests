import time
import uuid

from servertests import DataServerTestCase
from servertests.integration import container
from servertests.integration import container_of_length

from hamcrest import assert_that

class TestUserSearch(DataServerTestCase):

	def setUp(self):
		super(TestUserSearch, self).setUp()
		self.prefix = 'test.user'
		self.container = 'container-%s' % uuid.uuid1()
		self.users = [('%s.%s@nextthought.com' % (self.prefix, r), self.default_user_password) for r in xrange(15,19)]

	def _create_note_object(self, client, note, container):
		return client.create_object(note, objType='Note', container=container)

	def _create_users_notes(self, container):
		objects =[]
		for f in self.users:
			username = f[0]
			note = 'Fake note owned by %s' % username
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			objects.append(self.ds.create_note(note, self.container, adapt=True))
		return objects

	def _delete_user_notes(self, objects):
		it = iter(objects)
		for f in self.users:
			self.ds.clear_credentials()
			self.ds.set_credentials(f)
			self.ds.delete_object(it.next())

	def test_search_users(self):

		objects = self._create_users_notes(self.container)
		time.sleep(3)

		self.ds.set_credentials(self.users[0])

		result = self.ds.execute_user_search(self.prefix)
		assert_that(result, container())
		self.assertGreaterEqual(len(result['Items']), 3)

		result = self.ds.execute_user_search("%s.15" % self.prefix)
		assert_that(result, container_of_length(1))

		# not a reg exp
		result = self.ds.execute_user_search("%s.2*" % self.prefix)
		assert_that(result, container_of_length(0))

		result = self.ds.execute_user_search("%s.35" % self.prefix)
		assert_that(result, container_of_length(0))

		self._delete_user_notes(objects)

if __name__ == '__main__':
	import unittest
	unittest.main()
