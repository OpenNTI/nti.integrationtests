import time
import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import InstructorInfo
from nti.integrationtests.contenttypes import SectionInfo
from nti.integrationtests.contenttypes import ClassInfo

from hamcrest import not_none
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_length
from hamcrest import contains
from hamcrest import has_entry
from hamcrest import greater_than_or_equal_to

class TestBasicClassRoom(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	enrolled = ['test.user.%s@nextthought.com' % n for n in xrange(2, 6)]

	def setUp(self):
		super(TestBasicClassRoom, self).setUp()
		self.container = 'Classes'
		self.ds.set_credentials(self.owner)
	
	def test_create_class(self):
		provider = 'OU'
		
		ii = InstructorInfo(instructors = [self.owner[0]])
		si_name = 'Section.%s' % time.time()
		si = SectionInfo(ID = si_name,
						 description = si_name,
						 enrolled = self.enrolled,
						 instructor = ii)
		
		class_name = 'Class.%s' % time.time()
		ci = ClassInfo( ID = class_name,
						description = class_name,
						sections = [si],
						container = self.container );
						
		obj = self.ds.create_class(ci, provider)
		assert_that(obj.ID, is_(class_name))
		assert_that(obj.creator, is_('OU'))
		assert_that(obj.links, has_length(greater_than_or_equal_to(1)))
		assert_that(obj.links[0], has_entry('rel', 'edit'))
		assert_that(obj.ntiid, not_none())
		assert_that(obj.sections, has_length(1))
		
		si = obj.sections[0]
		assert_that(si.ID, is_(si_name))
		assert_that(si.ntiid, not_none())
		assert_that(si.enrolled, contains(*self.enrolled))
		assert_that(si.links, has_length(greater_than_or_equal_to(1)))
		assert_that(si.links[0], has_entry('rel', 'parent'))
		assert_that(si.provider, not_none())
		assert_that(si.instructor, not_none())
		
		ii = si.instructor
		assert_that(ii.instructors, contains(self.owner[0]))
		
if __name__ == '__main__':
	unittest.main()
