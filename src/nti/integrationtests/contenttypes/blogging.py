from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import SharableMixin
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

class PersonalBlog(DSObject, SharableMixin):
	
	DATASERVER_CLASS = 'PersonalBlog'
	MIME_TYPE = 'application/vnd.nextthought.forums.personalblog'
	
	_ds_field_mapping = {"topicCount":'TopicCount', "description": "description", 'title':'title' }
	_ds_field_mapping.update(DSObject._ds_field_mapping)
	_ds_field_mapping.update(SharableMixin._ds_field_mapping)

	_fields = {'topicCount':True, 'description':False, 'title':False}
	_fields.update(DSObject._fields)
	_fields.update(SharableMixin._fields)

class PersonalBlogEntry(DSObject, SharableMixin):
	DATASERVER_CLASS = 'PersonalBlogEntry'
	MIME_TYPE = 'application/vnd.nextthought.forums.personalblogentry'

	_ds_field_mapping = {'ID':'ID', "postCount":'PostCount', 'description':'description', 'likeCount':'LikeCount',
						 'tags':'tags', 'headline':'headline', 'href':'href' }
	_ds_field_mapping.update(DSObject._ds_field_mapping)
	_ds_field_mapping.update(SharableMixin._ds_field_mapping)

	_fields = {	'ID':True, 'tags' : (True, list), 'postCount':True, 'description':False, 'title':False, 'likeCount':True, 
				'headline':True, 'href':True}
	_fields.update(DSObject._fields)
	_fields.update(SharableMixin._fields)

class Post(DSObject, SharableMixin):
	
	DATASERVER_CLASS = 'Post'
	MIME_TYPE = 'application/vnd.nextthought.forums.post'
	
	_ds_field_mapping = {'title':'title', 'body':'body', 'tags':'tags' }
	_ds_field_mapping.update(DSObject._ds_field_mapping)
	_ds_field_mapping.update(SharableMixin._ds_field_mapping)

	_fields = {'title': False, 'body' : (False, list), 'tags' : (True, list)}
	_fields.update(DSObject._fields)
	_fields.update(SharableMixin._fields)
	
	def __setitem__(self, key, val):
		if key == 'body':
			self._assign_to_list(self._ds_field_mapping[key], val)
		else:
			super(Post, self).__setitem__(key, val)

class PersonalBlogEntryPost(Post):
	DATASERVER_CLASS = 'PersonalBlogEntryPost'
	MIME_TYPE = 'application/vnd.nextthought.forums.personalblogentrypost'
	
do_register_dsobjecs(dict(locals()).itervalues())
