#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import os
import six
import time
import random
import unittest
import collections

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import ClassInfo
from nti.integrationtests.contenttypes import SectionInfo
from nti.integrationtests.contenttypes import InstructorInfo
from nti.integrationtests.contenttypes.servicedoc import Link

from hamcrest import is_
from hamcrest import not_none
from hamcrest import contains
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_length
from hamcrest import has_property
from hamcrest import greater_than_or_equal_to

from nose.plugins.attrib import attr

@attr(level=3)
class TestBasicClassRoom(DataServerTestCase):

	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)
	enrolled = ['test.user.%s@nextthought.com' % n for n in xrange(2, 6)]

	def setUp(self):
		super(TestBasicClassRoom, self).setUp()
		self.container = 'Classes'
		self.ds.set_credentials(self.owner)
	
	def make_collecion(self, obj):
		if isinstance(obj, six.string_types):
			return [obj]
		return obj if isinstance(obj, collections.Iterable) else [obj]
		
	def create_class_info(self, instructors, no_sections, enrolled, class_name=None):
		enrolled = self.make_collecion(enrolled)
		instructors = self.make_collecion(instructors)
		ii = InstructorInfo(instructors = instructors)
		class_name = class_name or 'Class.%s' % time.time()

		sections = []
		for x in xrange(1, no_sections + 1):
			si_name = '%s.Section.%s' % (class_name, x)
			si = SectionInfo(ID = si_name,
							 description = si_name,
						 	 enrolled = enrolled,
						 	 instructor = ii)
			sections.append(si)
		
		
		ci = ClassInfo( ID = class_name,
						description = class_name,
						sections = sections,
						container = self.container )
		return (ci, ii, sections)
	
	def test_create_class(self):
		provider = 'OU'
		
		ci, _, sections = self.create_class_info(self.owner[0], 1, self.enrolled)
		si = sections[0]
		si_name = si.ID
		class_name = ci.ID
		
		obj = self.ds.create_class(ci, provider)
		__traceback_info__ = obj
		assert_that(obj.ID, is_(class_name))
		assert_that(obj, has_property( 'creator', is_('OU')))
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
		
		instructors = self.make_collecion(si.instructor.instructors)
		assert_that(instructors, contains(self.owner[0]))
		
	def test_create_class_and_resources(self):
		provider = 'OU'
		ci, _, sections= self.create_class_info(self.owner[0], 2, self.enrolled)
		ci = self.ds.create_class(ci, provider)
		
		source = os.path.join(os.path.dirname(__file__), "_class_image.jpg")
		entries = random.randint(3, 5)
		for x in xrange(1, entries +1):
			slug = 'class_image_%s.jpg' % x			
			self.ds.add_class_resource(source, provider, class_name=ci.ID, slug=slug)
		
		ci = self.ds.get_class(provider=provider, class_name=ci.ID)
		enclosures = 0 
		for d in ci.get_links():
			link = Link.new_from_dict(d)
			if link.rel == 'enclosure':
				enclosures = enclosures +1
		assert_that(entries, enclosures)
		
		source = os.path.join(os.path.dirname(__file__), "_section_doc.pdf")
		for s in sections:
			self.ds.add_class_resource(source, provider, class_name=ci.ID, section_name=s.ID, slug='section_doc.pdf')
		
		ci = self.ds.get_class(provider=provider, class_name=ci.ID)
		for s in ci.sections:
			found = False
			for d in s.get_links():
				link = Link.new_from_dict(d)
				if link.rel == 'enclosure':
					found = True
					break
			assert_that(found, is_(True))
		
if __name__ == '__main__':
	unittest.main()
