from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs
		
class QPart(DSObject):
	_ds_field_mapping = {'content':'content', 'hints':'hints', 'solutions':'solutions', 'explanation':'explanation'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'content':False, 'explanation':False, 'solutions' : (False, list), 'hints' : (False, list)}
	_fields.update(DSObject._fields)
	
	def __setitem__(self, key, val):
		if key in ('hints', 'solutions'):
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(QPart, self).__setitem__(key, val)

class QMathPart(QPart):
	DATASERVER_CLASS = 'MathPart'
	pass

class QNumericMathPart(QMathPart):
	DATASERVER_CLASS = 'NumericMathPart'
	pass
		
class QQuestion(DSObject):
	DATASERVER_CLASS = 'Question'
	MIME_TYPE = 'application/vnd.nextthought.naquestion'

	_ds_field_mapping = {'content':'content', 'parts':'parts'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'content':False, 'parts' : (False, list)}
	_fields.update(DSObject._fields)
	
	def __setitem__(self, key, val):
		if key in ('parts'):
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(QQuestion, self).__setitem__(key, val)
			
class QQuestionSet(DSObject):
	DATASERVER_CLASS = 'QuestionSet'
	MIME_TYPE = 'application/vnd.nextthought.naquestionset'

	_ds_field_mapping = {'questions':'questions'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'questions' : (False, list)}
	_fields.update(DSObject._fields)
	
	def __setitem__(self, key, val):
		if key in ('questions'):
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(QQuestionSet, self).__setitem__(key, val)
	
class QHint(DSObject):
	DATASERVER_CLASS = 'Hint'

class QTextHint(QHint):
	DATASERVER_CLASS = 'TextHint'
	
	_ds_field_mapping = {'value':'value'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'value' : False}
	_fields.update(DSObject._fields)

class QHTMLHint(QTextHint):
	DATASERVER_CLASS = 'HTMLHint'

class QSolution(DSObject):	
	_ds_field_mapping = {'weight':'weight'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'weight' : False}
	_fields.update(DSObject._fields)
	
class QMathSolution(QSolution):
	pass

class QNumericMathSolution(QMathSolution):
	DATASERVER_CLASS = 'NumericMathSolution'
	
	_ds_field_mapping = {'value':'value'}
	_ds_field_mapping.update(QMathSolution._ds_field_mapping)

	_fields = {'value' : False}
	_fields.update(QMathSolution._fields)
		
do_register_dsobjecs(dict(locals()).itervalues())
