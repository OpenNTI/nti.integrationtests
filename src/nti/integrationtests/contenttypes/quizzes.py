from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs
			
class QuizQuestion(DSObject):

	DATASERVER_CLASS = 'QuizQuestion'
	MIME_TYPE = 'application/vnd.nextthought.quizquestion'
	
	_ds_field_mapping = {'ID': 'ID', 'answers':'Answers', 'text':'Text'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'ID': True, 'answers': (False, list), 'text':False}
	_fields.update(DSObject._fields)
	
class Quiz(DSObject):

	DATASERVER_CLASS = 'Quiz'
	MIME_TYPE = 'application/vnd.nextthought.quiz'
	
	_ds_field_mapping = {'ID': 'ID', 'questions':'Items', 'href':'href'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'ID': True, 'questions': (False, dict), 'href': True}
	_fields.update(DSObject._fields)

	def get_question( self, qid ):
		questions = self.questions
		return questions.get( qid, None ) if questions else None
	
	def add_question(self, question):
		assert isinstance(question, QuizQuestion)
		questions = self.questions
		if questions is None:
			questions = {}
			self.__setitem__('questions', questions)
		questions[question.ID] = question
	
class QuizQuestionResponse(DSObject):

	DATASERVER_CLASS = 'QuizQuestionResponse'
	
	_ds_field_mapping = {'assessment': 'Assessment', 'question':'Question', 'response':'Response'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'assessment': True, 'question': True, 'response': False}
	_fields.update(DSObject._fields)
	
class QuizResult(DSObject):

	DATASERVER_CLASS = 'QuizResult'
	MIME_TYPE = 'application/vnd.nextthought.quizresult'
	
	_ds_field_mapping = {'ID': 'ID', 'answers':'Items', 'href':'href', 'quizid':'QuizID'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'ID': True, 'answers': (False, dict), 'href': True, 'quizid':True}
	_fields.update(DSObject._fields)
	
	def get_answer( self, qid ):
		answers = getattr(self, 'answers', None)
		if answers is not None:
			if isinstance(answers, list):
				for qqr in answers:
					q = qqr.question
					if q.ID == qid:
						return qqr
			else:
				answers.get( qid, None ) 
		return None
	
	def add_answer(self, qid, response):
		assert isinstance(response, QuizQuestionResponse)
		answers = getattr(self, 'answers', None)
		if answers is None:
			answers = {}
			self.__setitem__('answers', answers)
			
		if isinstance(answers, list):
			answers.append(response)
		else:
			answers[qid] = response

			
do_register_dsobjecs(dict(locals()).itervalues())
