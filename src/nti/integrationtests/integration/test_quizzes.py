import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import QTextHint
from nti.integrationtests.contenttypes import QQuestion
from nti.integrationtests.contenttypes import QQuestionSet
from nti.integrationtests.contenttypes import QNumericMathPart
from nti.integrationtests.contenttypes import QNumericMathSolution

#from hamcrest import (is_, is_not, assert_that)

class TestQuizzes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

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
