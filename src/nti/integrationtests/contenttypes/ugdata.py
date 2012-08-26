from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs
			
class Sharable(DSObject):

	_ds_field_mapping = {'sharedWith' : 'sharedWith'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'sharedWith' : (False,list)}
	_fields.update(DSObject._fields)

	def __setitem__(self, key, val):
		if key == 'sharedWith':
			self._assign_to_list(self._ds_field_mapping['sharedWith'], val)
		else:
			super(Sharable, self).__setitem__(key, val)

	def shareWith(self, targetOrTargets):
		targets = targetOrTargets
		if not isinstance(targets, list):
			targets = [targets]
		self.sharedWith.extend(targets)

	def revokeSharing(self, targetOrTargets):
		targets = targetOrTargets
		if not isinstance(targets, list):
			targets = [targets]

		for target in targets:
			self.sharedWith.remove(target)

	share_with = shareWith
	revoke_sharing = revokeSharing
	
class Threadable(DSObject):
	
	_ds_field_mapping = {'references':'references', 'inReplyTo':'inReplyTo'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'references' : (False, list), 'inReplyTo' : False}
	_fields.update(DSObject._fields)

	def __setitem__(self, key, val):
		if key == 'references':
			self._assign_to_list(self._ds_field_mapping['references'], val)
		else:
			super(Threadable, self).__setitem__(key, val)

class ContentRangeDescription(DSObject):
	DATASERVER_CLASS = 'ContentRangeDescription'
	pass

class DomContentRangeDescription(ContentRangeDescription):
	
	DATASERVER_CLASS = 'DomContentRangeDescription'
	
	_ds_field_mapping = {'start' : 'start', 'end':'end', 'ancestor':'ancestor'}
	_ds_field_mapping.update(ContentRangeDescription._ds_field_mapping)

	_fields = {'start' : False, 'end' : False, 'ancestor' : False}
	_fields.update(ContentRangeDescription._fields)
	
class ContentPointer(DSObject):
	pass

class DomContentPointer(ContentPointer):
	DATASERVER_CLASS = 'DomContentPointer'
	
	_ds_field_mapping = {'role' : 'role'}
	_ds_field_mapping.update(ContentPointer._ds_field_mapping)

	_fields = {'role' : False}
	_fields.update(ContentPointer._fields)

class ElementDomContentPointer(DomContentPointer):
	
	DATASERVER_CLASS = 'ElementDomContentPointer'
	
	_ds_field_mapping = {'elementId' : 'elementId', 'elementTagName':'elementTagName'}
	_ds_field_mapping.update(DomContentPointer._ds_field_mapping)

	_fields = {'elementId' : False, 'elementTagName': False}
	_fields.update(DomContentPointer._fields)
	
def create_artificial_applicable_range():
	result = ContentRangeDescription()
	return result

class Highlight(Sharable):
	
	DATASERVER_CLASS = 'Highlight'
	MIME_TYPE = 'application/vnd.nextthought.highlight'
	
	_ds_field_mapping = {'applicableRange':'applicableRange'}
	_ds_field_mapping.update(Sharable._ds_field_mapping)

	_fields = {'selectedText': False, 'applicableRange': False}
	_fields.update(Sharable._fields)

class Redaction(Highlight):
	
	DATASERVER_CLASS = 'Redaction'
	MIME_TYPE = 'application/vnd.nextthought.redaction'
	
	_ds_field_mapping = {'redactionExplanation':'redactionExplanation', 
						 'replacementContent' : 'replacementContent'}
	_ds_field_mapping.update(Highlight._ds_field_mapping)
	
	_fields = {'redactionExplanation': False, 'replacementContent': False}
	_fields.update(Highlight._fields)
	
class Note(Sharable, Threadable):

	DATASERVER_CLASS = "Note"
	MIME_TYPE = 'application/vnd.nextthought.note'

	_ds_field_mapping = {'href':'href', 'applicableRange':'applicableRange'}
	_ds_field_mapping.update(Sharable._ds_field_mapping)
	_ds_field_mapping.update(Threadable._ds_field_mapping)

	_fields = {'text': False, 'body': False, 'href':True, 'applicableRange': False}
	_fields.update(Sharable._fields)
	_fields.update(Threadable._fields)

class Change(DSObject):
	
	DATASERVER_CLASS = 'Change'
	MIME_TYPE = 'application/vnd.nextthought.change'

	_ds_field_mapping = {'changeType': 'ChangeType', 'item': 'Item', 'cid':'ID'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'changeType': True, 'item': True, 'cid': True}
	_fields.update(DSObject._fields)

class Canvas(DSObject):
	
	DATASERVER_CLASS = 'Canvas'
	MIME_TYPE = 'application/vnd.nextthought.canvas'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'shapeList':False}
	_fields.update(DSObject._fields)
	
class CanvasAffineTransform(DSObject):
	
	DATASERVER_CLASS = 'CanvasAffineTransform'
	MIME_TYPE = 'application/vnd.nextthought.canvasaffinetransform'
	
	_ds_field_mapping = {}
	
	_fields = {'a' : False, 'b' : False, 'c' : False, 'd' : False, 'tx' : False, 'ty' : False}
	
class CanvasShape(DSObject):
	
	DATASERVER_CLASS = 'CanvasShape'
	MIME_TYPE = 'application/vnd.nextthought.canvasshape'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'transform' : False}
	_fields.update(DSObject._fields)

class CanvasPolygonShape(CanvasShape):
	
	DATASERVER_CLASS = 'CanvasPolygonShape'
	MIME_TYPE = 'application/vnd.nextthought.canvaspolygonshape'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'sides' : False}
	_fields.update(CanvasShape._fields)

class CanvasTextShape(CanvasShape):
	
	DATASERVER_CLASS = 'CanvasTextShape'
	MIME_TYPE = 'application/vnd.nextthought.canvastextshape'
	
	_ds_field_mapping = {'modified':'Modified'}

	_fields = {	'text' : False, 'transform' : False, 'modified' : False, 'strokeOpacity' : 0,
				'strokeWidth' : False, 'fillRGBAColor': False }

do_register_dsobjecs(dict(locals()).itervalues())
