import time
import unittest
	
from hamcrest import assert_that
from hamcrest import is_not
from hamcrest import is_

from nti.integrationtests import DataServerTestCase
from nti.integrationtests.contenttypes import Quiz
from nti.integrationtests.contenttypes import QuizQuestion

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

if __name__ == '__main__':
	unittest.main()