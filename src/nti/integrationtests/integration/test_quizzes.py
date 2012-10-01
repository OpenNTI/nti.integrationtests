import unittest

from nti.integrationtests import DataServerTestCase

from hamcrest import (is_, is_not, assert_that)

class TestQuizzes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestQuizzes, self).setUp()
		
		self.container = self.generate_ntiid(provider=self.owner[0], nttype=self.TYPE_HTML)
		self.ds.set_credentials(self.owner)
		
