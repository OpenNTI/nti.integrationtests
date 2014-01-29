#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property

import os
import unittest

from nti.mechanize.config import read_config

class TestConfig(unittest.TestCase):
	
	def test_config(self):
		path = os.path.join(os.path.dirname(__file__), 'sample.cfg')
		context, runners = read_config(path, False)
		assert_that(context, has_property('rampup', is_(0)))
		assert_that(context, has_property('runners', is_(8)))
		assert_that(context, has_property('test_name', is_('sample')))
		assert_that(context, has_property('output_dir', is_('/tmp')))
		assert_that(context, has_property('serialize', is_(True)))
		assert_that(context, has_property('use_threads', is_(True)))
		assert_that(context, has_property('min_words', is_('10')))
		assert_that(context, has_property('max_words', is_('40')))

		assert_that(context, has_property('script_setup',
										  is_('nti.mechanize.tests.sample.script_setup')))

		assert_that(context, has_property('script_teardown',
										  is_('nti.mechanize.tests.sample.script_teardown')))

		assert_that(context, has_property('script_subscriber',
										  is_('nti.mechanize.tests.sample._listener')))

		assert_that(runners, has_length(1))
		assert_that(runners[0], has_property('context'))
		assert_that(runners[0], has_property('runners', is_(1)))
		assert_that(runners[0], has_property('max_iterations', is_(50)))
		assert_that(runners[0], has_property('group_name', is_('creation')))
		assert_that(runners[0], has_property('setup',
											 is_('nti.mechanize.tests.sample.setup')))
		assert_that(runners[0], has_property('teardown',
											 is_('nti.mechanize.tests.sample.teardown')))
		assert_that(runners[0], has_property('target',
											 is_('nti.mechanize.tests.sample.creation')))
		assert_that(runners[0], has_property('target_args', is_('("foo",1)')))
