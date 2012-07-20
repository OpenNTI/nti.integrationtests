from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes.ugdata import Threadable
from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

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
	

do_register_dsobjecs(dict(locals()).itervalues())
