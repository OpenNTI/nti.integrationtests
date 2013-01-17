import time
import uuid
import unittest

from nti.integrationtests import DataServerTestCase

from hamcrest import (assert_that, has_entry, has_key, has_length, greater_than)

class TestUserPreflightCreate(DataServerTestCase):

	headers = {'Origin':'https://mathcounts.nextthought.com'}

	def setUp(self):
		super(TestUserPreflightCreate, self).setUp()
		self.container = 'test.upc.container.%s' % time.time()

	def test_preflight_create(self):
		code =  str(uuid.uuid4()).split('-')[0]
		username = u'u' + code
		
		data = {"opt_in_email_communication":True, 'Username':username}
		d = self.ds.preflight_create_user(data)

		assert_that(d, has_key('AvatarURLChoices'))
		assert_that(d['AvatarURLChoices'], has_length(greater_than(0)))
		
		assert_that(d, has_key('ProfileSchema'))
		assert_that(d, has_key('href'))
		
		d = d.get('ProfileSchema')
		for key in ('Username', 'realname'):
			assert_that(d, has_key(key))
			assert_that(d[key], has_entry('required', True))
			assert_that(d[key], has_entry('name', key.lower()))
			assert_that(d[key], has_entry('type', 'string'))
			
		assert_that(d, has_key('password'))
		assert_that(d['password'], has_entry('required', True))
		assert_that(d['password'], has_entry('name', 'password'))
		
		for key in ('email', 'alias'):
			assert_that(d, has_key(key))
			assert_that(d[key], has_entry('name', key))
			assert_that(d[key], has_entry('type', 'string'))
	
		assert_that(d['email'], has_entry('required', True))
					
		for key in ('avatarURL', 'birthdate', 'invitation_codes', 'opt_in_email_communication', 'affiliation'):
			assert_that(d, has_key(key))
			assert_that(d[key], has_entry('required', False))
			assert_that(d[key], has_entry('name', key))
			
		assert_that(d['birthdate'], has_entry('type', 'date'))
		assert_that(d['invitation_codes'], has_entry('type', 'list'))
		assert_that(d['opt_in_email_communication'], has_entry('type', 'bool'))

	def _catch_test(self, data, msg):
		try:
			self.ds.preflight_create_user(data)
			self.fail(msg)
		except:
			pass
		
	def test_preflight_validate(self):
		self._catch_test({'Username':''}, 'Username cannot be empty')
		self._catch_test({'Username':'xx'}, 'Username too short')
		self._catch_test({'password':'xx'}, 'Password too short')
		self._catch_test({'password':'12345'}, 'Invalid password')
		self._catch_test({'email':'xx'}, 'Invalid email')
		self._catch_test({'role':'xx'}, 'Invalid role')
		self._catch_test({'birthdate':'xx'}, 'Invalid birthdate')
		
if __name__ == '__main__':
	unittest.main()
