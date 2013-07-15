from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs
		
class Device(DSObject):
	_ds_field_mapping = dict(**DSObject._ds_field_mapping)
	_ds_field_mapping.update({'id': 'ID', 'oid':'OID'})

	_fields = {'oid': True}
	_fields.update(DSObject._fields)
	
	DATASERVER_CLASS = 'Device'
	MIME_TYPE = 'application/vnd.nextthought.device'
	
	def __init__(self, *args, **kwargs):
		kwargs.pop('container', None)
		kwargs.pop('ContainerId', None)
		kwargs['container'] = 'Devices'
		super(Device, self).__init__(*args, **kwargs)
		
do_register_dsobjecs(dict(locals()).itervalues())
