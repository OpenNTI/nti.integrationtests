import os
import six
import urllib
import anyjson
import warnings
import collections
from urlparse import urljoin
from url_httplib import URLHttpLib

from nti.integrationtests.contenttypes.servicedoc import Link
from nti.integrationtests.contenttypes.servicedoc import Item
from nti.integrationtests.contenttypes.servicedoc import ROOT_ITEM
from nti.integrationtests.contenttypes.servicedoc import Workspace
from nti.integrationtests.contenttypes.servicedoc import Collection
from nti.integrationtests.contenttypes.servicedoc import EMPTY_CONTAINER_DICT
from nti.integrationtests.contenttypes.servicedoc import EMPTY_CONTAINER_ARRAY

from nti.integrationtests.contenttypes import Note
from nti.integrationtests.contenttypes import Canvas
from nti.integrationtests.contenttypes import DSObject
from nti.integrationtests.contenttypes import Sharable
from nti.integrationtests.contenttypes import Provider
from nti.integrationtests.contenttypes import Highlight
from nti.integrationtests.contenttypes import Redaction
from nti.integrationtests.contenttypes import FriendsList
from nti.integrationtests.contenttypes import adapt_ds_object
from nti.integrationtests.contenttypes import TranscriptSummary
from nti.integrationtests.contenttypes import CanvasPolygonShape
from nti.integrationtests.contenttypes import DynamicFriendsList
from nti.integrationtests.contenttypes import create_artificial_applicable_range

from hamcrest import assert_that, is_, is_not, none, instance_of

def get_root_item():
	return ROOT_ITEM

def get_link_from_dict(data):
	return Link.new_from_dict(data)

def get_item_from_dict(data):
	return Item.new_from_dict(data)

def get_workspaces(url, username, password='temp001'):
	"""
	Return the Workspace objects from the specified url
	url: dataserver URL
	user: User's name
	password: User's password
	"""

	httplib = URLHttpLib()
	rp = httplib.do_get(url, credentials=(username, password))
	data = httplib.deserialize(rp)

	result = []
	for item in data.get('Items', []):
		if not isinstance(item, dict): continue
		ws = Workspace.new_from_dict(item)
		result.append(ws)
	return result

def get_user_workspaces(url, username, password='temp001'):
	result = {}
	for ws in get_workspaces(url, username, password):
		result[ws.title] = ws
	return result

def _check_url(url):
	if url[-1] != '/':
		url += '/'
	return url

class DataserverClient(object):

	def __init__(self, endpoint, credentials=None, httplib=None):
		self.users_ws = {}
		self.credentials = credentials
		self.endpoint = _check_url(endpoint)
		self.httplib = httplib or URLHttpLib()

	def get_credentials(self):
		return self.credentials

	def set_credentials(self, credentials=None, user=None, password=None):
		self.credentials = credentials if credentials else (user, password)

	def clear(self):
		self.users_ws.clear()
		self.clear_credentials()

	def clear_credentials(self):
		self.credentials = None

	def create_note(self, data, container, inReplyTo=None, sharedWith=None, references=None, applicableRange=None,
					adapt=True, credentials=None, **kwargs):
		body = self.create_text_and_body(data)
		applicableRange = applicableRange or create_artificial_applicable_range()
		note = Note(body=body, container=container, inReplyTo=inReplyTo, sharedWith=sharedWith,
					applicableRange=applicableRange, references=references)
		return self.create_object(note, adapt=adapt, credentials=credentials, **kwargs)

	def create_text_and_body(self, data):
		if isinstance(data, six.string_types) or isinstance(data, DSObject):
			body = [data]
		elif isinstance(data, list):
			body = data
		elif isinstance(data, collections.Iterable):
			body = list(data)
		else:
			body = [data]
		return body

	createNote = create_note

	def create_highlight(self, selectedText, container, applicableRange=None, adapt=True, credentials=None, **kwargs):
		applicableRange = applicableRange or create_artificial_applicable_range()
		highlight = Highlight(selectedText=selectedText, container=container, applicableRange=applicableRange, **kwargs)
		return self.create_object(highlight, adapt=adapt, **kwargs)

	def create_redaction(self, selectedText, container, applicableRange=None,
						 replacementContent=None, redactionExplanation=None, adapt=True, credentials=None, **kwargs):
		applicableRange = applicableRange or create_artificial_applicable_range()
		redaction = Redaction(selectedText=selectedText, container=container, replacementContent=replacementContent,
							  redactionExplanation=redactionExplanation, applicableRange=applicableRange)
		return self.create_object(redaction, adapt=adapt, **kwargs)

	def create_canvas(self, sides, tx, ty, container, store=False, adapt=True, credentials=None, **kwargs):
		shape = CanvasPolygonShape(sides=sides, container=container, **kwargs)
		canvas = Canvas(shapeList=[shape], container=container, **kwargs)
		return self.create_object(canvas, credentials=credentials, adapt=adapt, **kwargs) if store else canvas

	def create_DFL_with_name_and_friends(self, name, friends, realname=None, credentials=None, adapt=True, **kwargs):
		dfl = DynamicFriendsList(name=name, friends=friends, realname=realname or name)
		return self.create_friends_list(dfl, credentials=credentials, adapt=adapt, **kwargs)

	def create_friends_list_with_name_and_friends(self, name, friends, credentials=None, adapt=True, **kwargs):
		fl = FriendsList(name=name, friends=friends)
		return self.create_friends_list(fl, credentials=credentials, adapt=adapt, **kwargs)

	def create_friends_list(self, obj, credentials=None, adapt=True, **kwargs):
		assert_that(obj, instance_of(FriendsList), 'must provide a valid DataServer object')
		collection, _ = self._get_collection(name='FriendsLists', credentials=credentials)
		return self._post_to_collection(obj, collection, credentials, adapt=adapt, **kwargs)

	def get_friends_lists(self, credentials=None, adapt=True, **kwargs):
		collection, _ = self._get_collection(name='FriendsLists', credentials=credentials)

		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, collection.href)

		rp = self.httplib.do_get(url, credentials, **kwargs)
		assert_that(rp.status_int, is_(200), 'invalid status code getting friends lists')

		data = self.httplib.deserialize(rp)
		data = data.get('Items', {})
		result = adapt_ds_object(data) if adapt else data
		return result

	createFriendsListWithNameAndFriends = create_friends_list_with_name_and_friends

	# ------------------------

	def get_user_generated_data(self, container, workspace=None, credentials=None, adapt=True, **kwargs):
		data = self._get_container_item_data(container=container, link_rel='UserGeneratedData', workspace=workspace,
											 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data

	def get_recursive_stream_data(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_item_data(container=container, link_rel='RecursiveStream', workspace=workspace,
											 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data

	def get_ugd_and_recursive_stream_ata(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_item_data(container=container, link_rel='UserGeneratedDataAndRecursiveStream', workspace=workspace,
											 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data

	def get_recursive_user_generated_data(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_item_data(container=container, link_rel='RecursiveUserGeneratedData', workspace=workspace,
											 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data

	getUserGeneratedData = get_user_generated_data
	getRecursiveStreamData = get_recursive_stream_data

	# ------------------------

	def get_object(self, obj=None, link=None, credentials=None, adapt=True, **kwargs):
		
		if link is None:
			assert_that(obj, instance_of(DSObject), 'must provide a valid DataServer object')
			
		credentials = self._credentials_to_use(credentials)
		href = link or obj.get_edit_link()
		url = urljoin(self.endpoint, href)
		__traceback_info__ = url, credentials, obj
		rp = self.httplib.do_get(url, credentials, **kwargs)
		
		assert_that(rp.status_int, is_(200), "invalid status code getting object at '%s'" % href)

		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data

	def create_object(self, obj, credentials=None, name='Pages', workspace=None, adapt=True, **kwargs):
		assert_that(obj, instance_of(DSObject), 'must provide a valid DataServer object')
		assert_that(obj.container, is_not(none()), 'must provide a valid container')
		pages, _ = self._get_collection(name=name, workspace=workspace, credentials=credentials)
		result = self._post_to_collection(obj, pages, credentials, adapt=adapt, **kwargs)
		return result

	def update_object(self, obj=None, link=None, credentials=None, adapt=True, **kwargs):

		if not link:
			assert_that(obj, instance_of(DSObject), 'must provide a valid DataServer object')

		href = link or obj.get_edit_link()
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)
		__traceback_info__ = url, credentials, obj

		rp = self.httplib.do_put(url, credentials=credentials, data=self.object_to_persist(obj), **kwargs)
		assert_that(rp.status_int, is_(200), 'invalid status code while updating an object')

		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data

	def delete_object(self, obj=None, link=None, credentials=None, **kwargs):

		if not link:
			assert_that(obj, instance_of(DSObject), 'must provide a valid DataServer object')

		href = link or obj.get_delete_link()
		assert_that(href, is_not(none()), 'no delete link was provided')

		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)

		rp = self.httplib.do_delete(url, credentials=credentials, **kwargs)
		assert_that(rp.status_int, is_(204), 'invalid status code while deleting an object')

		return None

	def share_object(self, obj, targets, credentials=None, adapt=True, **kwargs):
		# Some clients use this API wrong, passing in credentials
		# instead of targets. Detect that.
		if isinstance( targets, tuple ) and len(targets) == 2 and credentials is None and '@' not in targets[1]:
			warnings.warn( "Incorrect API usage: passed credentials for targets" )
			targets = [targets[0]]

		if isinstance(obj, Sharable):
			obj.share_with(targets)
		else:
			if not isinstance(targets, list):
				targets = [targets]

			obj['sharedWith'].extend(targets)

		return self.update_object(obj, credentials=credentials, adapt=adapt, **kwargs)

	def unshare_object(self, obj, targets, credentials=None, adapt=True, **kwargs):
		if isinstance(obj, Sharable):
			obj.revoke_sharing(targets)
		else:
			if not isinstance(targets, list):
				targets = [targets]

			for target in targets:
				obj['sharedWith'].remove(target)

		return self.update_object(obj, credentials=credentials, adapt=adapt, **kwargs)

	def like_object(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_like_link()
		return self._like_fav_op(href, 'like', credentials=credentials, adapt=adapt, **kwargs)

	def unlike_object(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_unlike_link()
		return self._like_fav_op(href, 'unlike', credentials=credentials, adapt=adapt, **kwargs)

	def fav_object(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_favorite_link()
		return self._like_fav_op(href, 'favorite', credentials=credentials, adapt=adapt, **kwargs)

	def unfav_object(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_unfavorite_link()
		return self._like_fav_op(href, 'unfavorite', credentials=credentials, adapt=adapt, **kwargs)
	
	def flag_object(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_flag_link()
		return self._like_fav_op(href, 'flag', credentials=credentials, adapt=adapt, **kwargs)
	
	def replies(self, obj, credentials=None, adapt=True, **kwargs):
		href = obj.get_replies_link()
		assert_that(href, is_not(none()), "no '%s' href was provided for replies" )
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)
		rp = self.httplib.do_get(url, credentials=credentials, **kwargs)
		assert_that(rp.status_int, is_(200), "invalid status code object in replied operation")
		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data
	
		return self._like_fav_op(href, 'replies', credentials=credentials, status=204, **kwargs)

	def _like_fav_op(self, href, operation, credentials=None, adapt=True, **kwargs):
		assert_that(href, is_not(none()), "no '%s' href was provided" % operation)
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)

		rp = self.httplib.do_post(url, credentials=credentials, **kwargs)
		assert_that(rp.status_int, is_(200), "invalid status code object in '%s' operation" % operation)

		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data

	likeObject = like_object
	shareObject = share_object
	unlikeObject = unlike_object
	createObject = create_object

	# ------------------------

	def get_transcript(self, container, room_id, name='Pages', workspace=None, credentials=None, adapt=True, **kwargs):

		credentials = self._credentials_to_use(credentials)
		data = self.get_user_generated_data(container=container, workspace=workspace, credentials=credentials, adapt=True)
		for item in data.get('Items',[]):
			if not isinstance(item, TranscriptSummary):
				continue

			if not item.container == room_id:
				continue

			href = item.get_link('transcript')
			assert_that(href, is_not(none()), 'could not find a transcript link for %s' % room_id)

			url = urljoin(self.endpoint, href)
			rp = self.httplib.do_get(url, credentials, **kwargs)
			assert_that(rp.status_int, is_(200), 'invalid status code while getting transcript data')

			data = self.httplib.deserialize(rp)
			return adapt_ds_object(data) if adapt else data

		return None

	getTranscript = get_transcript

	# ------------------------

	def _do_search(self, link, query, ntiid=None, credentials=None, adapt=True, **kwargs):

		credentials = self._credentials_to_use(credentials)
		collection, _ = self._get_collection(credentials=credentials)

		link = collection.get_link(link)
		url = _check_url(urljoin(self.endpoint, link.href))
		if ntiid:
			url = _check_url(url + urllib.quote(ntiid))
		url = url + urllib.quote(query)

		rp = self.httplib.do_get(url, credentials, **kwargs)
		assert_that(rp.status_int, is_(200), 'invalid status code while searching content')

		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data

	def search_user_content(self, query, credentials=None, adapt=True, **kwargs):
		result = self._do_search('UGDSearch', query, None, credentials, adapt, **kwargs)
		return result

	searchUserContent = search_user_content

	def unified_search(self, query, ntiid=None, credentials=None, adapt=True, **kwargs):
		result = self._do_search('UnifiedSearch', query, ntiid, credentials, adapt, **kwargs)
		return result

	unifiedSearch = unified_search

	def get_user_object(self, user=None, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		user = user or credentials[0]
		data = self.execute_user_search(user, credentials, adapt, **kwargs)
		return data['Items'][0] if 'Items' in data and data['Items'] else data

	getUserObject = get_user_object

	def execute_user_search(self, search, credentials=None, adapt=True, **kwargs):

		credentials = self._credentials_to_use(credentials)
		link, _ = self._get_user_search_link(credentials=credentials)
		url = _check_url(urljoin(self.endpoint, link.href)) + search

		rp = self.httplib.do_get(url, credentials, **kwargs)
		if rp.status_int == 404:
			return EMPTY_CONTAINER_ARRAY

		assert_that(rp.status_int, is_(200), 'invalid status code while getting user object(s)')

		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data

	executeUserSearch = execute_user_search

	def _get_user_search_link(self, credentials=None):

		credentials = self._credentials_to_use(credentials)
		ds_ws = self._get_or_parse_user_doc(credentials)
		assert_that(ds_ws, is_not(none()), "could not find service document for '%s'" % credentials[0])

		ws = ds_ws.get('Global', None)
		assert_that(ws, is_not(none()), "could not find Global workspace for '%s'" % credentials[0])

		link = ws.get_link('UserSearch')
		assert_that(link, is_not(none()), "could not find a UserSearch link in Global workspace for '%s'" % credentials[0])

		return (link, ws)

	# ------------------------

	def create_provider(self, name, credentials=None):
		credentials = self._credentials_to_use(credentials)
		provider = Provider(name=name)
		return provider

	def create_class(self, classinfo, provider, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		collection, _ = self._get_collection(name=provider, workspace='providers', credentials=credentials)
		result = self._post_to_collection(classinfo, collection, credentials, adapt=adapt, **kwargs)
		return result

	def get_class(self, provider, class_name, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		class_info = self._get_container(class_name, name=provider, workspace='providers',
										 credentials=credentials, always_new=True, **kwargs)
		return adapt_ds_object(class_info) if isinstance(class_info, dict) and adapt else class_info

	def add_class_resource(	self, source_file, provider, class_name, section_name=None,
							content_type=None, credentials=None, slug=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		class_info = self.get_class(provider, class_name, credentials=credentials, adapt=True)
		assert_that(class_info, is_not(none()), "could not find a class with name '%s'" % class_name)

		href = class_info.href
		if section_name:
			section = class_info.get_section(section_name)
			assert_that(section, is_not(none()), "could not find a section with name '%s'" % section_name)
			href = section.href

		location, slug = self._post_raw_content(href, source_file, content_type, slug=slug, **kwargs)
		return (location, slug)

	# ------------------------

	def get_user_workspace(self, credentials=None):
		ds_ws = self._get_or_parse_user_doc(credentials)
		return ds_ws.get(credentials[0], None)

	def get_collection_data(self, name='Pages', workspace=None, credentials=None, validate=False, **kwargs):
		collection, ws = self._get_collection(name, workspace, credentials, validate, **kwargs)
		collection = self._parse_collection_data(collection.href, credentials) if ws and collection else None
		if ws and collection:
			ws.add_collection(collection)
		return collection

	def object_to_persist(self, obj):
		if hasattr(obj, 'toDataServerObject'):
			obj = obj.toDataServerObject()
		result = anyjson.dumps(obj)
		return result

	# ------------------------

	def _get_collection(self, name='Pages', workspace=None, credentials=None, validate=True, **kwargs):

		credentials = self._credentials_to_use(credentials)
		workspace = workspace or credentials[0]
		ds_ws = self._get_or_parse_user_doc(credentials)
		if validate:
			assert_that(ds_ws, is_not(none()), "could not find service document for '%s'" % credentials[0])

		ws = ds_ws.get(workspace, None) if ds_ws else None
		if validate:
			assert_that(ws, is_not(none()), "could not find '%s' workspace" % workspace)

		collection = ws.get_collection(name) if ws else None
		if validate:
			assert_that(collection, is_not(none()), "could not find '%s' collection" % name)

		return (collection, ws)

	def _get_container(	self, container, name='Pages', workspace=None, credentials=None, validate=True,
					 	always_new=False, **kwargs):
		"""
		return Item object associated withe specified workspace/collection
		container: Item container id
		name: collection name
		workspace: workspace name:
		credentials: user credentials
		validate: validate flag
		"""
		credentials = self._credentials_to_use(credentials)
		collection, _ = self._get_collection(name=name, workspace=workspace,
											 credentials=credentials, validate=validate, **kwargs)
		if not collection.has_item(container) or always_new:
			collection = self.get_collection_data(name=name, workspace=workspace,
												  credentials=credentials, validate=validate, **kwargs)

		item = collection.get_item(container)
		return item

	def _get_container_item_data(self, container, link_rel, name='Pages', workspace=None, credentials=None,
								 validate=True, **kwargs):
		"""
		return raw data (dict) associated withe specified workspace/collection for the specified container using
		the specified link rel

		container: Item container id
		link_rel: link relation
		name: collection name
		workspace: workspace name:
		credentials: user credentials
		validate: validate flag
		"""
		credentials = self._credentials_to_use(credentials)
		item = self._get_container(	container=container, name=name, workspace=workspace,
									credentials=credentials, validate=validate)

		if not item:
			return EMPTY_CONTAINER_DICT

		link = item.get_link(link_rel)
		if validate:
			assert_that(link, is_not(none()), "could not find '%s' link" % link_rel)

		elif not link:
			return EMPTY_CONTAINER_DICT

		url = urljoin(self.endpoint, link.href)
		rp = self.httplib.do_get(url, credentials, **kwargs)

		# check for empty reply from the server
		if rp.status_int == 404:
			return EMPTY_CONTAINER_DICT

		assert_that(rp.status_int, is_(200), "invalid status code getting '%s'" % link_rel)
		return self.httplib.deserialize(rp)

	def _post_to_collection(self, obj, collection, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, collection.href)
		rp = self.httplib.do_post(url, credentials=credentials, data=self.object_to_persist(obj), **kwargs)
		assert_that(rp.status_int, is_(201), 'invalid status code while posting an object')

		data = self.httplib.deserialize(rp)
		result = adapt_ds_object(data) if adapt else data
		return result

	def _post_raw_content(self, href, source, content_type=None, slug=None, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		slug = slug or os.path.basename(source)
		url = urljoin(self.endpoint, href)

		rp = self.httplib.do_upload_resource(url, credentials=credentials, source_file=source,
											 content_type=content_type, headers= {'slug' : slug }, **kwargs)
		assert_that(rp.status_int, is_(201), 'invalid status code while posting raw content')

		headers = rp.headers
		return (headers.get('location', None), slug)

	def _get_or_parse_user_doc(self, credentials=None):
		credentials = self._credentials_to_use(credentials)
		if credentials[0] not in self.users_ws:
			ds = get_user_workspaces(self.endpoint, credentials[0], credentials[1])
			self.users_ws[credentials[0]] = ds
		return self.users_ws[credentials[0]]

	def _parse_collection_data(self, href, credentials=None, **kwargs):
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)

		rp = self.httplib.do_get(url, credentials, **kwargs)
		assert_that(rp.status_int, is_(200), 'invalid status code while getting collection data')

		data = self.httplib.deserialize(rp)
		return Collection.new_from_dict(data) if data else None

	def _credentials_to_use(self, credentials):
		return credentials or self.credentials

	# ------------------------

	def create_user(self, username, password, email, realname=None, opt_in_email_communication=False, adapt=True, **kwargs):
		params = dict(kwargs)
		params['email'] = email
		params['Username'] = username
		params['password'] = password
		params['realname'] = realname or username
		params['opt_in_email_communication'] = opt_in_email_communication
		
		# remove any None argument
		for k,v in list(params.items()):
			if v is None:
				params.pop(k)
				
		payload = anyjson.dumps(params)
		
		href = "users/@@account.create"
		url = urljoin(self.endpoint, href)
		rp = self.httplib.do_post(url, data=payload)
		assert_that(rp.status_int, is_(201), 'invalid status code while trying to create a user')
		
		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data
		
	def resolve_user(self, username, credentials=None, adapt=True, **kwargs):
		credentials = self._credentials_to_use(credentials)
		
		href = "ResolveUser/%s" % username
		url = urljoin(self.endpoint, href)
		rp = self.httplib.do_get(url, credentials, **kwargs)
		assert_that(rp.status_int, is_(200), 'invalid status while resolving user')
			
		data = self.httplib.deserialize(rp)
		return adapt_ds_object(data) if adapt else data
		
	# ------------------------

	createCanvas = create_canvas
	updateObject = update_object
	unshareObject = unshare_object
	setCredentials = set_credentials
	createHighlight = create_highlight
	getFriendsLists = get_friends_lists
	objectToPersist = object_to_persist
	clearCredentials = clear_credentials
	createFriendsList = create_friends_list
	createTextAndBody = create_text_and_body

# -------------------------------

if __name__ == '__main__':
	end_point = 'http://localhost:8081/dataserver2'
	cl = DataserverClient(end_point)
	cl.set_credentials(user='test.user.1@nextthought.com', password='temp001')
