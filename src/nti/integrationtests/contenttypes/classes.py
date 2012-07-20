from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

class InstructorInfo(DSObject):
	
	DATASERVER_CLASS = 'InstructorInfo'
	MIME_TYPE = 'application/vnd.nextthought.instructorinfo'
	
	_ds_field_mapping = {'instructors':'Instructors'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'instructors' : (False, list)}
	_fields.update(DSObject._fields)

	def __setitem__(self, key, val):
		if key == 'instructors':
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(InstructorInfo, self).__setitem__(key, val)
				
class ClassSectionMixin(DSObject):
	
	DEFAULT_ACCEPTS = ['image/*', 'application/pdf', 'application/vnd.nextthought.classscript']
	
	_ds_field_mapping = {'description':'Description', 'ID':'ID', 'ntiid': 'NTIID', 'accepts':'accepts', 'href':'href'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {	'description': False, 'ID':False, 'ntiid': True, 'accepts': (False, list), 'href':False}
	_fields.update(DSObject._fields)

	def __getitem__(self, key):
		if key == 'NTIID': key = 'ntiid'
		result = super(ClassSectionMixin, self).__getitem__(key)
		if key == 'accepts' and not result:
			result = self.DEFAULT_ACCEPTS
		return result
	
	def __setitem__(self, key, val):
		if key == 'accepts':
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(ClassSectionMixin, self).__setitem__(key, val)
			
class SectionInfo(ClassSectionMixin):
	
	DATASERVER_CLASS = 'SectionInfo'
	MIME_TYPE = 'application/vnd.nextthought.sectioninfo'
	
	_ds_field_mapping = {'closeDate':'CloseDate', 'enrolled':'Enrolled',  'instructor':'InstructorInfo', \
						 'openDate':'OpenDate', 'provider':'Provider', 'sessions':'Sessions'}
	_ds_field_mapping.update(ClassSectionMixin._ds_field_mapping)

	_fields = {	'enrolled' : (False, list), 'closeDate' : False, 'instructor': False, 'openDate' : False,\
				'provider': True, 'sessions' : (False, list)}
	_fields.update(ClassSectionMixin._fields)
	
	def __getitem__(self, key):
		if key == 'name': key = 'ID'
		if key == 'instructorInfo': key = 'instructor'
		return super(SectionInfo, self).__getitem__(key)
	
	def __setitem__(self, key, val):
		if key == 'name': key = 'ID'
		if key == 'instructorInfo': key = 'instructor'
		super(SectionInfo, self).__setitem__(key, val)
			
class ClassInfo(ClassSectionMixin):
	
	DATASERVER_CLASS = 'ClassInfo'
	MIME_TYPE = 'application/vnd.nextthought.classinfo'
	
	_ds_field_mapping = {'sections':'Sections'}
	_ds_field_mapping.update(ClassSectionMixin._ds_field_mapping)

	_fields = {	'sections' : (False, list) }
	_fields.update(ClassSectionMixin._fields)
	
	def get_section(self, section_id):
		for s in self.sections:
			if s.ID == section_id:
				return s
		return None
	
	def __setitem__(self, key, val):
		if key == 'sections':
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(ClassInfo, self).__setitem__(key, val)
		
class Provider(DSObject):
	
	DATASERVER_CLASS = 'Provider'
	
	_ds_field_mapping = {'name':'ID'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {	'name' :  False }
	_fields.update(DSObject._fields)
			

do_register_dsobjecs(dict(locals()).itervalues())
