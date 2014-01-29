#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than
from hamcrest import has_property

import os
import unittest

from ..runner import run

class TestRunner(unittest.TestCase):
	
	def test_config(self):
		path = os.path.join(os.path.dirname(__file__), 'sample.cfg')
		context, groups, elapsed = run(path)
		assert_that(elapsed, greater_than(0))

		assert_that(context, has_property('opened', is_(True)))
		assert_that(context, has_property('closed', is_(True)))

		assert_that(groups, has_length(1))
		assert_that(groups[0], has_property('results', has_length(1)))
		result = groups[0].results[0]
		assert_that(result, has_property('listened', is_(True)))
