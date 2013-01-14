import time
import unittest

from nti.integrationtests import DataServerTestCase

from hamcrest import (assert_that,  has_entry, has_key)

class TestUserPreflightCreate(DataServerTestCase):

	headers = {'Origin':'mathcounts.nextthought.com'}

	def setUp(self):
		super(TestUserPreflightCreate, self).setUp()
		self.container = 'test.upc.container.%s' % time.time()

	def test_preflight_create(self):
		data = {"opt_in_email_communication":True}
		d = self.ds.preflight_create_user(data)
		assert_that(d, has_key('AvatarURLChoices'))
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
		
		for key in ('affiliation', 'email', 'alias'):
			assert_that(d, has_key(key))
			assert_that(d[key], has_entry('required', False))
			assert_that(d[key], has_entry('name', key))
			assert_that(d[key], has_entry('type', 'string'))
	
		for key in ('avatarURL', 'birthdate', 'invitation_codes', 'opt_in_email_communication'):
			assert_that(d, has_key(key))
			assert_that(d[key], has_entry('required', False))
			assert_that(d[key], has_entry('name', key))
			
		assert_that(d['birthdate'], has_entry('type', 'date'))
		assert_that(d['invitation_codes'], has_entry('type', 'list'))
		assert_that(d['opt_in_email_communication'], has_entry('type', 'bool'))

if __name__ == '__main__':
	unittest.main()
#
#http://localhost:8081/dataserver2/users/@@account.preflight.create
#{"opt_in_email_communication":true,"realname":"Carlos Sanchez"}:
#
#{"opt_in_email_communication":true,"realname":"Carlos Sanchez","email":"maletas@ou.edu"}:
#
#{"opt_in_email_communication":true,"realname":"Carlos Sanchez","email":"maletas@ou.edu","password":"saulo213"}:
#
#{"opt_in_email_communication":false,"realname":"Carlos Sanchez","email":"maletas@ou.edu","password":"saulo213","Username":"maletas"}:
#
#{.'AvatarURLChoices': [],
# 'ProfileSchema': {'Username': {'min_length': 5,
#                                'name': 'username',
#                                'readonly': False,
#                                'required': True,
#                                'type': 'string'},
#                   'affiliation': {'min_length': 0,
#                                   'name': 'affiliation',
#                                   'readonly': False,
#                                   'required': False,
#                                   'type': 'string'},
#                   'alias': {'min_length': 0,
#                             'name': 'alias',
#                             'readonly': False,
#                             'required': False,
#                             'type': 'string'},
#                   'avatarURL': {'min_length': 0,
#                                 'name': 'avatarURL',
#                                 'readonly': False,
#                                 'required': False},
#                   'birthdate': {'min_length': None,
#                                 'name': 'birthdate',
#                                 'readonly': False,
#                                 'required': False,
#                                 'type': 'date'},
#                   'email': {'min_length': 0,
#                             'name': 'email',
#                             'readonly': False,
#                             'required': False,
#                             'type': 'string'},
#                   'invitation_codes': {'name': 'invitation_codes',
#                                        'readonly': False,
#                                        'required': False,
#                                        'type': 'list'},
#                   'opt_in_email_communication': {'min_length': None,
#                                                  'name': 'opt_in_email_communication',
#                                                  'readonly': False,
#                                                  'required': False,
#                                                  'type': 'bool'},
#                   'password': {'min_length': None,
#                                'name': 'password',
#                                'readonly': False,
#                                'required': True},
#                   'realname': {'min_length': 0,
#                                'name': 'realname',
#                                'readonly': False,
#                                'required': True,
#                                'type': 'string'}},
# 'Username': 'carloszxz',
# 'href': '/dataserver2/users/@@account.preflight.create'}