import time
import unittest
	
from hamcrest import assert_that
from hamcrest import is_not
from hamcrest import is_

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Quiz
from nti.integrationtests.contenttypes import QuizQuestion
from nti.integrationtests.contenttypes import QuizResult
from nti.integrationtests.contenttypes import QuizQuestionResponse

class TestQuizzes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestQuizzes, self).setUp()
		
		self.container = 'test.user.container.%s' % time.time()
		self.ds.set_credentials(self.owner)
		
	def test_creating_a_quizz(self):
		qq  = QuizQuestion(ID='Question.1', text='Is true?', answers=['True', '1.0', '1'])
		q = Quiz(ID="MyQuiz", container=self.container)
		q.add_question(qq)
		obj = self.ds.create_object(q)
		
		assert_that(obj, is_not(None))
		assert_that(obj.ID, is_('MyQuiz'))
		assert_that(obj.href, is_not(None))
		
		qq = obj.get_question('Question.1')
		assert_that(qq, is_not(None))
		assert_that(qq.text, is_('Is true?'))
		assert_that(qq.answers, is_(['True', '1.0', '1']))
		
	@unittest.expectedFailure
	def test_creating_a_quizz_and_result(self):
		self.container = 'quizzes'
		qq  = QuizQuestion(ID='q1', text='Area of an 8x8 square?', answers=['64', '64.0'])
		q = Quiz(ID="MyGeomQuiz", container=self.container)
		q.add_question(qq)
		self.ds.create_object(q)
		
		qqr = QuizQuestionResponse(question="q1", response="64")
		qr = QuizResult(quizid="MyGeomQuiz", container=self.container)
		qr.add_answer('q1', qqr)
		
		obj = self.ds.create_object(qr)
		assert_that(obj, is_not(None))
		
	
if __name__ == '__main__':
	unittest.main()