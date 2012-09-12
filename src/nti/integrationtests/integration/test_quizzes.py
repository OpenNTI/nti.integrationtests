import unittest

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Quiz
from nti.integrationtests.contenttypes import QuizQuestion
from nti.integrationtests.contenttypes import QuizResult
from nti.integrationtests.contenttypes import QuizQuestionResponse

from hamcrest import (is_, is_not, assert_that)

class TestQuizzes(DataServerTestCase):
	
	owner = ('test.user.1@nextthought.com', DataServerTestCase.default_user_password)

	def setUp(self):
		super(TestQuizzes, self).setUp()
		
		self.container = self.generate_ntiid(provider=self.owner[0], nttype=self.TYPE_HTML)
		self.ds.set_credentials(self.owner)
		
	def xtest_creating_a_quizz(self):
		
		qq  = QuizQuestion(ID='Question.1', text='Is true?', answers=['True', '1.0', '1'])
		q = Quiz(container=self.container)
		q.add_question(qq)
		obj = self.ds.create_object(q)
		
		assert_that(obj, is_not(None))
		assert_that(obj.ID, is_not(None))
		assert_that(obj.href, is_not(None))
		
		qq = obj.get_question('Question.1')
		assert_that(qq, is_not(None))
		assert_that(qq.text, is_('Is true?'))
		assert_that(qq.answers, is_(['True', '1.0', '1']))
		
	def test_creating_a_quizz_and_result(self):

		qq_1 = QuizQuestion(ID='q1', text='Area of an 8x8 square?', answers=['$64$', '$64.0$'])
		qq_2 = QuizQuestion(ID='q2', text='Summ?', answers=["\[\sum_{i=1}^{10} t_i\]"])
		qq_3 = QuizQuestion(ID='q3', text='Int?', answers=["\[\int_0^\infty e^{-x}\,\mathrm{d}x\]"])
		
		q = Quiz(container=self.container)
		q.add_question(qq_1)
		q.add_question(qq_2)
		q.add_question(qq_3)
		q = self.ds.create_object(q)
		
		quizid = q.ID
		assert_that(qq_1, is_not(None))
			
		qqr_1 = QuizQuestionResponse(question="q1", response="$64$")
		qqr_2 = QuizQuestionResponse(question="q2", response="$\[\sum_{i=1}^{10} t_i\]$")
		qqr_3 = QuizQuestionResponse(question="q3", response="\[\int_0^\infty e^{x}\,\mathrm{d}x\]")
		
		qr = QuizResult(quizid=quizid, container=self.container)
		qr.add_answer('q1', qqr_1)
		qr.add_answer('q2', qqr_2)
		qr.add_answer('q3', qqr_3)
		
		obj = self.ds.create_object(qr)
		assert_that(obj, is_not(None))
		
		qqr = obj.get_answer('q1')
		assert_that(qqr, is_not(None))
		assert_that(qqr.assessment, is_(True))
		
		qqr = obj.get_answer('q2')
		assert_that(qqr.assessment, is_(True))
		
		qqr = obj.get_answer('q3')
		assert_that(qqr.assessment, is_(False))
	
if __name__ == '__main__':
	unittest.main()