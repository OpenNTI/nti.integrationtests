import pdb
import pprint
import inspect
import UserDict
import collections

#########################

def toExternalObject(obj):
	if isinstance(obj, DSObject):
		return obj.toDataServerObject()
	return obj if isinstance(obj, collections.Mapping) else None

to_external_object = toExternalObject

#########################

def getter(name, def_value=None):
	def function(self):
		if self.really_contains( name ):
			return self[name]
		self.really_set( name, def_value() if isinstance(def_value,type) else def_value )
		return self[name]
	return function

def setter(name):
	def function(self, val):
		self[name] = val
	return function

class MetaDSObject(type):
	
	def __new__(mcs, clsname, clsbases, clsdict):
		t = type.__new__(mcs, clsname, clsbases, clsdict)
		fields = getattr(t, '_fields', None)
		if fields is not None:
			# _fields is a mapping between field name and
			# a value, either boolean for readonly, or a
			# tuple (readonly, default_value). def_value my be a type
			# to construct a new one on access.
			# create properties for our fields
			for name, value in fields.items():
				readonly = value
				def_value = None
				if isinstance( value, tuple ):
					readonly, def_value = value

				if readonly:
					setattr(t, name, property(getter(name, def_value)))
				else:
					setattr(t, name, property(getter(name, def_value), setter(name)))
		# create a reverse mapping
		mapping = getattr(t, '_ds_field_mapping', None)
		if mapping:
			inverted = {}
			for key, val in mapping.items():
				inverted[val] = key
			t._inverted_ds_field_mapping = inverted
		return t

# -----------------------------------

link_types = ('edit', )
	

class DSObject(object, UserDict.DictMixin):

	__metaclass__ = MetaDSObject

	# defines a mapping from testing framework fields -> internal dataserver fields
	_ds_field_mapping = {'id' : 'OID', 'container': 'ContainerId', 'creator': 'Creator', 
						 'lastModified': 'Last Modified', 'links':'Links', 'mimeType': 'MimeType',
						 'ntiid': 'NTIID'}

	# mapping of fields we expose to readonly
	_fields = {	'container': True, 'id' : True, 'creator' : True, 'lastModified' : True, 
				'links' : True, 'mimeType': True, 'ntiid': True}

	def __init__(self, data=None, **kwargs):
		self._data = data or {}

		# set our class name if we now it
		if hasattr(self, "DATASERVER_CLASS"):
			self._data['Class'] = getattr( self, 'DATASERVER_CLASS' )
			
		if hasattr(self, "MIME_TYPE"):
			self._data['MimeType'] = getattr( self, 'MIME_TYPE' )
			
		if kwargs:
			for field in self._fields:
				if field in kwargs:
					val = kwargs[field]
					field = self._ds_field_mapping.get(field, field)
					self._data[field] = val

	# Oddly, we claim to contain everything
	# we have a field for, even if it has never been set.
	# Our [] implementation will return a value for
	# everything we declare a field for, even if never set.
	# These all need to be consistent: __contains__, keys,
	# iterkeys(), items, __getitem__, __setitem__

	def __contains__( self, key ):
		return key in self._fields

	def really_contains( self, key ):
		return key in self._data

	def really_set( self, key, value ):
		self._data[key] = value

	def __getitem__(self, key):
		if key == 'oid' or key == 'OID':
			key = 'id'
		elif key == 'ContainerId' or key == 'containerId':
			key = 'container'
			
		if key not in self._fields:
			raise KeyError('Unsupported key %s' % key)

		key = self._ds_field_mapping[key] if key in self._ds_field_mapping else key
		return self._data[key] if key in self._data else None

	def _field_readonly( self, field ):
		value = self._fields[field]
		if isinstance( value, tuple ):
			value = value[0]
		return value

	def __setitem__(self, key, val):
		if key not in self._fields or self._field_readonly( key ):
			raise KeyError('Cannot set uneditable field %s' % key)

		key = self._ds_field_mapping[key] if key in self._ds_field_mapping else key
		self._data[key] = val

	def __delitem__(self, key):
		raise RuntimeError("cannot delete property")

	def keys(self):
		return self._fields.keys()
	
	def toDataServerObject(self):
		external = {}
		for key, val in self._data.iteritems():
			
			if val is None or key is None:
				continue
			
			# val may be an array in which case we need to call toDataserverObject
			# on each value
		
			if isinstance(val, list):
				val = [v.toDataServerObject() if hasattr(v, 'toDataServerObject') else v for v in val]
			elif hasattr(val, 'toDataServerObject'):
				val = val.toDataServerObject()

			external[key] = val
		return external

	to_data_server_object = toDataServerObject
	
	def update_from_data_server_obbject(self, dsDict):
		self._data = adapt_ds_object(dsDict)
	updateFromDataServerObject = update_from_data_server_obbject
	
	def pprint(self, stream=None):
		data = self.to_data_server_object()
		pprint.pprint(data, stream=stream)
		
	def _assign_to_list(self, mapkey, val, defType=list):
		if isinstance(val, list):
			collection = val
		elif isinstance(val, basestring):
			collection = [val]
		elif isinstance(val, collections.Iterable):
			collection = self._data[mapkey] if mapkey in self._data else defType()
			collection.extend(val)
		else:
			collection = [val]
		self._data[mapkey] = collection

	def __str__( self ):
		return "%s(%s)" % (self.__class__.__name__,self._data)

	def __repr__( self ):
		return self.__str__()

	def get_edit_link(self):
		return self.get_link('edit')
	
	def get_delete_link(self):
		return self.get_edit_link()
	
	def get_link(self, link_type = None):
		if link_type and hasattr(self, 'links'):
			links = self.links or []
			for link in links:
				if link.get('rel', None) == link_type:
					return link.get('href', None)
		return None
	
	def get_links(self):
		return getattr(self, 'links', [])
	
	@classmethod
	def fields(cls):
		"""
		return the fields for this object
		"""
		return list(cls._fields.keys())

collections.MutableMapping.register( DSObject )

# -----------------------------------

class Community(DSObject):
	
	DATASERVER_CLASS = 'Community'
	
	_ds_field_mapping = {'name': 'Username', 'alias':'alias', 'avatarURL':'avatarURL'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'name': True, 'alias': False, 'avatarURL': False}
	_fields.update(DSObject._fields)
	
	def __getitem__(self, key):
		if key == 'Username' or key == 'username':
			key = 'name'
		return super(Community, self).__getitem__(key)
	
	def __setitem__(self, key, val):
		if key == 'name' or key == 'username' or key == 'Username':
			self._data[self._ds_field_mapping['name']] = val
		else:
			super(Community, self).__setitem__(key, val)
			
class FriendsList(Community):
	
	DATASERVER_CLASS = 'FriendsList'
	MIME_TYPE = 'application/vnd.nextthought.friendslist'
	
	_ds_field_mapping = {'friends' : 'friends'}
	_ds_field_mapping.update(Community._ds_field_mapping)

	_fields = {'friends' : False}
	_fields.update(Community._fields)

	def __setitem__(self, key, val):
		if key == 'friends':
			self._assign_to_list(self._ds_field_mapping['friends'], val)
		else:
			super(FriendsList, self).__setitem__(key, val)

class User(Community):
	
	DATASERVER_CLASS = 'User'
	
	_ds_field_mapping = {'communities': 'Communities', 'notificationCount':'NotificationCount', \
						 'presence':'Presence', 'lastLoginTime':'lastLoginTime', 'accepting':'accepting', \
						 'following': 'following', 'ignoring':'ignoring', 'realname':'realname'}
	_ds_field_mapping.update(Community._ds_field_mapping)

	_fields = {	'communities' : False, 'notificationCount':True, 'presence':True, 'lastLoginTime':False,
				'accepting': False, 'following': False, 'ignoring':False, 'realname': False}
	_fields.update(Community._fields)

	def __getitem__(self, key):
		if key == 'notificationCount' or key == 'NotificationCount':
			key = 'notificationCount'
		return super(User, self).__getitem__(key)
	
	def __setitem__(self, key, val):
		if key == 'communities' or key == 'Communities':
			self._assign_to_list(self._ds_field_mapping['communities'], val)
		elif key == 'accepting':
			self._assign_to_list(self._ds_field_mapping['accepting'], val)
		elif key == 'ignoring':
			self._assign_to_list(self._ds_field_mapping['ignoring'], val)
		else:
			super(User, self).__setitem__(key, val)
			
# -----------------------------------

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
	
# -----------------------------------

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

class Highlight(Sharable):
	
	DATASERVER_CLASS = 'Highlight'
	MIME_TYPE = 'application/vnd.nextthought.highlight'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(Sharable._ds_field_mapping)

	_fields = {'startHighlightedText': False}
	_fields.update(Sharable._fields)

# -----------------------------------

class Note(Sharable, Threadable):

	DATASERVER_CLASS = "Note"
	MIME_TYPE = 'application/vnd.nextthought.note'

	_ds_field_mapping = {}
	_ds_field_mapping.update(Sharable._ds_field_mapping)
	_ds_field_mapping.update(Threadable._ds_field_mapping)

	_fields = {'text': False, 'body': False}
	_fields.update(Sharable._fields)
	_fields.update(Threadable._fields)

# -----------------------------------

class Change(DSObject):
	
	DATASERVER_CLASS = 'Change'
	MIME_TYPE = 'application/vnd.nextthought.change'

	_ds_field_mapping = {'changeType': 'ChangeType', 'item': 'Item'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'changeType': True, 'item': True}
	_fields.update(DSObject._fields)

# -----------------------------------

class Canvas(DSObject):
	
	DATASERVER_CLASS = 'Canvas'
	MIME_TYPE = 'application/vnd.nextthought.canvas'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'shapeList':False}
	_fields.update(DSObject._fields)

# -----------------------------------

class CanvasAffineTransform(DSObject):
	
	DATASERVER_CLASS = 'CanvasAffineTransform'
	MIME_TYPE = 'application/vnd.nextthought.canvasaffinetransform'
	
	_ds_field_mapping = {}
	
	_fields = {'a' : False, 'b' : False, 'c' : False, 'd' : False, 'tx' : False, 'ty' : False}
	
# -----------------------------------

class CanvasShape(DSObject):
	
	DATASERVER_CLASS = 'CanvasShape'
	MIME_TYPE = 'application/vnd.nextthought.canvasshape'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'transform' : False}
	_fields.update(DSObject._fields)

# -----------------------------------

class CanvasPolygonShape(CanvasShape):
	
	DATASERVER_CLASS = 'CanvasPolygonShape'
	MIME_TYPE = 'application/vnd.nextthought.canvaspolygonshape'
	
	_ds_field_mapping = {}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'sides' : False}
	_fields.update(CanvasShape._fields)

# -----------------------------------

class RoomInfo(Threadable):
	
	DATASERVER_CLASS = 'RoomInfo'
	
	_ds_field_mapping = {'active':'Active', 'messageCount':'MessageCount', 'moderated':'Moderated', 'occupants':'Occupants'}
	_ds_field_mapping.update(Threadable._ds_field_mapping)

	_fields = {'active': True, 'messageCount' : True, 'moderated': True, 'occupants' : (True, list)}
	_fields.update(Threadable._fields)

	def __getitem__(self, key):
		if key == 'message_count' or key == 'MessageCount':
			key = 'messageCount'
		return super(RoomInfo, self).__getitem__(key)
	
	def __setitem__(self, key, val):
		if key == 'occupants' or key == 'Occupants':
			self._assign_to_list(self._ds_field_mapping['occupants'], val)
		else:
			super(RoomInfo, self).__setitem__(key, val)
			
class TranscriptSummary(DSObject):
	
	DATASERVER_CLASS = 'TranscriptSummary'
	MIME_TYPE = 'application/vnd.nextthought.transcriptsummary'
	
	_ds_field_mapping = {'contributors':'Contributors', 'nitid':'NTIID', 'roomInfo':'RoomInfo'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'contributors' : (True, list), 'nitid' : True, 'roomInfo': True}
	_fields.update(DSObject._fields)

	def __setitem__(self, key, val):
		if key == 'contributors':
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(TranscriptSummary, self).__setitem__(key, val)
	
	
# -----------------------------------

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
	
	_ds_field_mapping = {'ID': 'ID', 'questions':'Items'}
	_ds_field_mapping.update(DSObject._ds_field_mapping)

	_fields = {'ID': True, 'questions': (False, dict)}
	_fields.update(DSObject._fields)

	def get_question( self, qid ):
		questions = self.questions
		return questions.get( qid, None )
	
	def add_question(self, question):
		assert isinstance(question, QuizQuestion)
		questions = self.questions
		questions[question.ID] = question
	
# -----------------------------------

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
			
# -----------------------------------

DS_TYPE_REGISTRY = {}
MIME_TYPE_REGISTRY = {}

for v in dict(locals()).itervalues():
	if inspect.isclass(v) and issubclass(v, DSObject):
		if hasattr(v, 'DATASERVER_CLASS'):
			DS_TYPE_REGISTRY[v.DATASERVER_CLASS] = v
			
		if hasattr(v, 'MIME_TYPE'):
			MIME_TYPE_REGISTRY[v.MIME_TYPE] = v
			

def do_adaptation(registry, dsobject, key):
	value = dsobject.get(key, None)
	clazz = registry.get(value, None) if value else None
	return clazz(data=dsobject) if clazz else None

def adapt_ds_object(dsobject):

	# if we arent a list or a dict we are just a plain value
	if not (isinstance(dsobject, list) or isinstance(dsobject, dict)):
		return dsobject

	# if our ds object is an array we need to convert all the subparts
	if isinstance(dsobject, list):
		objects = []
		for dsobj in dsobject:
			objects.append(adapt_ds_object(dsobj))
		return objects

	# most of the time we get back dictionaries
	# our dictionaries can wrap objects in two ways.  Via Items and Item
	# adapt those as necessary
	# its not just items and item we need to adapt.  Some things like
	# friends lists need each key adapted.
	for key in dsobject:
		dsobject[key] = adapt_ds_object(dsobject[key])

	# any children we have have been adapted.  Now adapt ourselves
	
	adapted_object = do_adaptation(MIME_TYPE_REGISTRY, dsobject, 'MimeType')
	adapted_object = adapted_object or do_adaptation(DS_TYPE_REGISTRY, dsobject, 'Class')
	adapted_object = adapted_object or dsobject
	
	return adapted_object

adaptDSObject = adapt_ds_object
