#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import QTextHint
from nti.integrationtests.contenttypes import QQuestion
from nti.integrationtests.contenttypes import QQuestionSet
from nti.integrationtests.contenttypes import QNumericMathPart
from nti.integrationtests.contenttypes import QNumericMathSolution

from nose.plugins.attrib import attr
#from hamcrest import (is_, is_not, assert_that)

@attr(level=3)
class TestQuizzes(DataServerTestCase):
	
	owner = ('test.user.1', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestQuizzes, self).setUp()
		
		self.container = self.generate_ntiid(provider=self.owner[0], nttype=self.TYPE_HTML)
		self.ds.set_credentials(self.owner)
		
	@unittest.expectedFailure
	def test_creating_a_quizz(self):
		
		p = QNumericMathPart(content='MyPart', explanation='MyExplanation', 
							 solutions=[QNumericMathSolution(value=46.0, weight=1.0)],
							 hints=[QTextHint(value='MyHint')])
		qq  = QQuestion(content='MyQuestion.1', parts=[p])
		quiz = QQuestionSet(container=self.container, questions=[qq])
		self.ds.create_object(quiz)
		#print obj
		
if __name__ == '__main__':
	unittest.main()
