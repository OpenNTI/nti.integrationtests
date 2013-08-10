from __future__ import print_function, unicode_literals

from nti.integrationtests.contenttypes._dsobject import DSObject
from nti.integrationtests.contenttypes._dsobject import SharableMixin
from nti.integrationtests.contenttypes._dsobject import do_register_dsobjecs

class Forum(DSObject, SharableMixin):

	DATASERVER_CLASS = 'Forum'
	MIME_TYPE = 'application/vnd.nextthought.forums.forum'

	_ds_field_mapping = {"topicCount":'TopicCount', "description": "description", 'title':'title',
						 'newestDescendantCreatedTime':'NewestDescendantCreatedTime',
						 'newestDescendant':'NewestDescendant' }
	_ds_field_mapping.update(DSObject._ds_field_mapping)
	_ds_field_mapping.update(SharableMixin._ds_field_mapping)

	_fields = {'topicCount':True, 'description':False, 'title':False,
			   'newestDescendant':True, 'newestDescendantCreatedTime':True}
	_fields.update(DSObject._fields)
	_fields.update(SharableMixin._fields)

class CommunityForum(Forum):
	MIME_TYPE = 'application/vnd.nextthought.forums.communityforum'

class ForumACE(DSObject):

	DATASERVER_CLASS = 'ForumACE'
	MIME_TYPE = 'application/vnd.nextthought.forumace'

	_ds_field_mapping = {"action":'Action', 'entities':'Entities', 'permission':'Permission'}

	_fields = {'action':False, 'entities':(False, list), 'permission':False}

class ACLCommunityForum(CommunityForum):

	DATASERVER_CLASS = 'ACLCommunityForum'
	MIME_TYPE = 'application/vnd.nextthought.forums.aclcommunityforum'

	_ds_field_mapping = {"acl":'ACL'}
	_ds_field_mapping.update(CommunityForum._ds_field_mapping)

	_fields = {'acl':(False, list)}
	_fields.update(CommunityForum._fields)

class PersonalBlog(Forum):
	
	DATASERVER_CLASS = 'PersonalBlog'
	MIME_TYPE = 'application/vnd.nextthought.forums.personalblog'
	
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
	
	_ds_field_mapping = {'title':'title', 'body':'body', 'tags':'tags', 'href':'href' }
	_ds_field_mapping.update(DSObject._ds_field_mapping)
	_ds_field_mapping.update(SharableMixin._ds_field_mapping)

	_fields = {'title': False, 'body' : (False, list), 'tags' : (True, list), 'href':True}
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

class PersonalBlogComment(Post):
	DATASERVER_CLASS = 'PersonalBlogComment'
	MIME_TYPE = 'application/vnd.nextthought.forums.personalblogcomment'

do_register_dsobjecs(dict(locals()).itervalues())
