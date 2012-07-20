from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

class PageInfo(DSObject):
	
	DATASERVER_CLASS = 'PageInfo'
	MIME_TYPE = 'application/vnd.nextthought.pageinfo'
	
	_ds_field_mapping = {'id' : 'ID', 'lastModified': 'Last Modified', 'links':'Links', 'mimeType': 'MimeType',
						 'ntiid': 'NTIID', 'href':'href', 'sharingPreference':'sharingPreference' }

	_fields = {	'id' : True, 'lastModified' : True, 'links' : True, 'mimeType': True, 'ntiid': True,
				'href': True, 'sharingPreference':False}
				
class SharingPreference(DSObject):
	
	DATASERVER_CLASS = 'SharingPagePreference'
	
	_ds_field_mapping = {'provenance':'Provenance', 'state':'State', 'sharedWith':'sharedWith'}

	_fields = {'sharedWith' : (False, list), 'state' : False, 'provenance': True}

do_register_dsobjecs(dict(locals()).itervalues())
