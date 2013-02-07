from __future__ import print_function, unicode_literals

import six
import pprint
import inspect
import UserDict
import collections
from persistent import Persistent

# Global class registration

DS_TYPE_REGISTRY = {}
MIME_TYPE_REGISTRY = {}

def do_register_dsobjecs(classes):
	for v in classes:
		if inspect.isclass(v) and issubclass(v, DSObject):
			clazz = getattr(v, 'DATASERVER_CLASS', None)
			if clazz and clazz not in DS_TYPE_REGISTRY:
				DS_TYPE_REGISTRY[clazz] = v
			
			mt = getattr(v, 'MIME_TYPE', None)
			if mt:
				MIME_TYPE_REGISTRY[mt] = v
				
# Externalization

def toExternalObject(obj):
	
	def recall( obj ):
		if hasattr(obj, 'toDataServerObject'):
			result = obj.toDataServerObject()
		elif isinstance(obj, six.string_types):
			result = unicode(obj)
		elif isinstance(obj, collections.Mapping):
			result = {}
			for key, value in obj.iteritems():
				result[key] = recall( value )					
			result = None if not result else result
		elif isinstance(obj, (collections.Set, collections.Sequence)):
			result = [recall(v) for v in obj]
		else:
			result = obj
		return result
		
	return recall(obj)

to_external_object = toExternalObject

# DataServer object definition

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

link_types = ('edit', 'like', 'unlike', 'favorite', 'unfavorite')
	
class SharableMixin(object):

	_ds_field_mapping = {'sharedWith' : 'sharedWith'}
	_fields = {'sharedWith' : (False, list)}

	def __setitem__(self, key, val):
		if key == 'sharedWith':
			self._assign_to_list(self._ds_field_mapping['sharedWith'], val)
		else:
			super(SharableMixin, self).__setitem__(key, val)

	def shareWith(self, targetOrTargets, reset=False):
		targets = targetOrTargets
		if not isinstance(targets, list):
			targets = [targets]
		
		if not reset:
			self.sharedWith.extend(targets)
		else:
			self.sharedWith = targets

	def revokeSharing(self, targetOrTargets):
		targets = targetOrTargets
		if not isinstance(targets, list):
			targets = [targets]

		for target in targets:
			self.sharedWith.remove(target)

	share_with = shareWith
	revoke_sharing = revokeSharing
	
class DSObject(Persistent, UserDict.DictMixin):

	__metaclass__ = MetaDSObject

	# defines a mapping from testing framework fields -> internal dataserver fields
	_ds_field_mapping = {'id' : 'OID', 'container': 'ContainerId', 'creator': 'Creator', 
						 'lastModified': 'Last Modified', 'links':'Links', 'mimeType': 'MimeType',
						 'ntiid': 'NTIID', 'createdTime':'CreatedTime'}

	# mapping of fields we expose to readonly
	_fields = {	'container': True, 'id' : True, 'creator' : True, 'lastModified' : True, 
				'links' : True, 'mimeType': True, 'ntiid': True, 'createdTime': True}

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
			new_val = toExternalObject(val)
			if new_val is not None:
				external[key] = new_val
		return external

	to_data_server_object = toDataServerObject
	
	def update_from_data_server_obbject(self, dsDict):
		self._data = adapt_ds_object(dsDict)
	updateFromDataServerObject = update_from_data_server_obbject
	
	def pprint(self, stream=None):
		data = self.toDataServerObject()
		pprint.pprint(data, stream=stream)
		
	def _assign_to_list(self, mapkey, val, defType=list):
		if isinstance(val, list):
			collection = val
		elif isinstance(val, six.string_types):
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
	
	def get_flag_link(self):
		return self.get_link('flag')
	
	def get_flag_metoo_link(self):
		return self.get_link('flag.metoo')
	
	def get_like_link(self):
		return self.get_link('like')
	
	def get_favorite_link(self):
		return self.get_link('favorite')
	
	def get_unlike_link(self):
		return self.get_link('unlike')
	
	def get_unfavorite_link(self):
		return self.get_link('unfavorite')
	
	def get_replies_link(self):
		return self.get_link('replies')
	
	def get_link(self, link_type = None):
		if link_type and hasattr(self, 'links'):
			links = self.links or ()
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
				
def do_adaptation(registry, dsobject, key):
	mimetype = dsobject.get('MimeType', None)
	value = dsobject.get(key, None)
	constructor = registry.get(value, None) if value else None
	if mimetype == 'application/vnd.nextthought.friendslist':
		from nti.integrationtests.contenttypes import FriendsList, DynamicFriendsList
		constructor = DynamicFriendsList if dsobject.get('IsDynamicSharing', False) else FriendsList	
	return constructor(data=dsobject) if constructor else None

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

	