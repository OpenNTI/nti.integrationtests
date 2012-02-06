import os
import json
import time
import pprint
import requests
import warnings
import collections
from io import BytesIO
from urlparse import urljoin

from requests.models import Response

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
from nti.integrationtests.contenttypes import FriendsList
from nti.integrationtests.contenttypes import adapt_ds_object
from nti.integrationtests.contenttypes import TranscriptSummary
from nti.integrationtests.contenttypes import CanvasPolygonShape

# -----------------------------------

DEBUG_GET = False

# -----------------------------------

class DeclarationError(AssertionError):
	def __init__(self, message='', args=None, code=None):
		super(DeclarationError, self).__init__(message, args)
		self.code = code
	
	@property
	def status_code(self):
		return self.code
	
	def __str__(self):
		return self.message
	
	def __repr__(self):
		return "DeclarationError(%s,%s,%s)" % (self.message, self.args, self.code)
		
def check_that(expr, message='', args=None, code=None):
	if not expr:
		raise DeclarationError(message=message, args=args, code=code)
	
# -----------------------------------

def get_root_item():
	return ROOT_ITEM

def get_link_from_dict(data):
	return Link.new_from_dict(data)

def get_item_from_dict(data):
	return Item.new_from_dict(data)

def get_encoding(obj):
	data = None
	
	if isinstance(obj, Response):
		data = obj.headers.get('content-type', None)
	elif isinstance(obj, dict):
		data = obj.get('content-type', None)
	
	data = str(data) if data else 'UTF-8'
	if data.find('charset=') != -1:
		data = data[data.find('charset=') + 8:]
	return data
	
def do_get(url, auth, trx=True):	
	rp = requests.get(url, auth=auth)
	raw_content = rp.content
	encoding = get_encoding(rp)
	
	if DEBUG_GET:
		try:
			dt = json.loads(raw_content, encoding=encoding) if raw_content else {}
		except Exception, e:
			dt = {'Exception': e}
		d = {'data':dt, 'url':url, 'auth':auth, 'raw': raw_content}
		pprint.pprint(d)
		
	data = json.loads(raw_content, encoding=encoding) if trx else raw_content
	return (rp, data, encoding)

def get_workspaces(url, username, password='temp001'):
	"""
	Return the Workspace objects from the specified url
	url: dataserver URL
	user: User's name
	password: User's password
	"""
	
	_, data, _ = do_get(url, auth=(username, password))
	
	#import pprint
	#pprint.pprint(data)
	
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

# -----------------------------------

def _check_url(url):
	if url[-1] != '/':
		url += '/'
	return url

# -----------------------------------

class DataserverClient(object):

	def __init__(self, endpoint, credentials=None):
		self.users_ws = {}
		self.credentials = credentials
		self.endpoint = _check_url(endpoint)

	def get_credentials(self):
		return self.credentials
	
	def set_credentials(self, credentials=None, user=None, password=None):
		self.credentials = credentials if credentials else (user, password)

	def clear(self):
		self.users_ws.clear()
		self.clear_credentials()
		
	def clear_credentials(self):
		self.credentials = None

	# --------------
	
	def create_note(self, data, container, inReplyTo=None, sharedWith=None, adapt=True, **kwargs):
		body = self.create_text_and_body(data)
		note = Note(body=body, container=container, inReplyTo=inReplyTo, sharedWith=sharedWith, **kwargs)
		return self.create_object(note, adapt=adapt, **kwargs)
	
	def create_text_and_body(self, data):
		if isinstance(data, basestring) or isinstance(data, DSObject):
			body = [data]
		elif isinstance(data, list):
			body = data
		elif isinstance(data, collections.Iterable):
			body = list(data)
		else:
			body = [data]
		return body
	
	createNote = create_note
	
	# --------------
	
	def create_highlight(self, startHighlightedText, container, adapt=True, **kwargs):
		highlight = Highlight(startHighlightedText=startHighlightedText, container=container, **kwargs)
		return self.create_object(highlight, adapt=adapt, **kwargs)

	def create_canvas(self, sides, tx, ty, container, store=False, adapt=True, **kwargs):
		shape = CanvasPolygonShape(sides=sides, container=container, **kwargs)
		canvas = Canvas(shapeList=[shape], container=container, **kwargs)
		return self.create_object(canvas, adapt=adapt, **kwargs) if store else canvas

	def create_friends_list_with_name_and_friends(self, name, friends, credentials=None, adapt=True):
		return self.create_friends_list(FriendsList(name=name, friends=friends), credentials=credentials, adapt=adapt)

	def create_friends_list(self, obj, credentials=None, adapt=True):
		check_that(isinstance(obj, FriendsList), "must provide a valid DataServer object", obj)
		collection, _ = self._get_collection(name='FriendsLists', credentials=credentials)
		return self._post_to_collection(obj, collection, credentials, adapt=adapt)
	
	def get_friends_lists(self, credentials=None, adapt=True):
		
		collection, _ = self._get_collection(name='FriendsLists', credentials=credentials)
		
		auth = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, collection.href)
		
		rp, data, encoding = do_get(url, auth, False)
		check_that(rp.status_code == 200, 'invalid status code getting friends lists', code=rp.status_code)
		data = json.loads(data, encoding=encoding)
		data = data.get('Items', {})
		return adapt_ds_object(data) if adapt else data
	
	createFriendsListWithNameAndFriends = create_friends_list_with_name_and_friends
		
	# --------------
	
	def get_user_generated_data(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_raw_item_data(container=container, link_rel='UserGeneratedData', workspace=workspace,
												 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data

	def get_recursive_stream_data(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_raw_item_data(container=container, link_rel='RecursiveStream', workspace=workspace,
												 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data
	
	
	def get_recursive_user_generated_data(self, container, workspace=None, credentials=None, adapt=True):
		data = self._get_container_raw_item_data(container=container, link_rel='RecursiveUserGeneratedData', workspace=workspace,
												 credentials=credentials, validate=True)
		return adapt_ds_object(data) if adapt else data
	
	getUserGeneratedData = get_user_generated_data
	getRecursiveStreamData = get_recursive_stream_data
	
	# --------------
	
	def get_object(self, obj_id, credentials=None, adapt=True):
		collection, _ = self._get_collection(name='Objects', workspace='Global', credentials=credentials)
		auth = self._credentials_to_use(credentials)
		url = _check_url(urljoin(self.endpoint, collection.href)) + obj_id
		rp, data, encoding = do_get(url, auth, False)
		check_that(rp.status_code == 200, "invalid status code getting object with id '%s'" % obj_id, obj_id, rp.status_code)
		data = json.loads(data, encoding=encoding)
		return adapt_ds_object(data) if adapt else data
	
	def create_object(self, obj, credentials=None, adapt=True, **kwargs):
		check_that(isinstance(obj, DSObject), "must provide a valid DataServer object", obj)
		check_that(obj.container, "must provide a valid container", obj)
		pages, _ = self._get_collection(name='Pages', credentials=credentials)
		return self._post_to_collection(obj, pages, credentials, adapt=adapt)
	
	def update_object(self, obj, link=None, credentials=None, adapt=True):
		
		if not link:
			check_that(isinstance(obj, DSObject), "must provide a valid DataServer object", obj)
		
		href = link or obj.get_edit_link()
		auth = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)
		rp = requests.put(url, auth=auth, data=self.object_to_persist(obj))
		check_that(rp.status_code == 200, 'invalid status code while updating an object', obj, rp.status_code)
		
		loaded = json.loads(rp.content, encoding=get_encoding(rp))
		return adapt_ds_object(loaded) if adapt else loaded
	
	def delete_object(self, obj, link=None, credentials=None):
		
		if not link:
			check_that(isinstance(obj, DSObject), "must provide a valid DataServer object", obj)
		
		href = link or obj.get_delete_link()
		check_that(href, "no delete link was provided", obj)
		
		auth = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)
		rp = requests.delete(url, auth=auth)
		check_that(rp.status_code == 204, 'invalid status code while deleting an object', obj, rp.status_code)
		
		return None
	
	def share_object(self, obj, targets, credentials=None, adapt=True):
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

		return self.update_object(obj, credentials=credentials, adapt=adapt)

	def unshare_object(self, obj, targets, credentials=None, adapt=True):
		if isinstance(obj, Sharable):
			obj.revoke_sharing(targets)
		else:
			if not isinstance(targets, list):
				targets = [targets]

			for target in targets:
				obj['sharedWith'].remove(target)

		return self.update_object(obj, credentials=credentials, adapt=adapt)
	
	shareObject = share_object
	createObject = create_object
	
	# --------------
	
	def get_transcript(self, container, room_id, name='Pages', workspace=None, credentials=None, adapt=True):
		
		credentials = self._credentials_to_use(credentials)
		data = self.get_user_generated_data(container=container, workspace=workspace, credentials=credentials, adapt=True)
		for item in data.get('Items',[]):
			if not isinstance(item, TranscriptSummary):
				continue
		
			if not item.container == room_id:
				continue
			
			href = item.get_link('transcript')
			check_that( href, 'could not find a transcript link for %s' % room_id, room_id)
			
			url = urljoin(self.endpoint, href)
			rp, data, encoding = do_get(url, credentials, False)
			check_that(rp.status_code == 200, 'invalid status code while getting transcript data', href, rp.status_code)
			
			trx = json.loads(data, encoding=encoding)
			return adapt_ds_object(trx) if adapt else trx
		
		return None
	
	getTranscript = get_transcript
	
	# -------------
	
	def search_user_content(self, query, credentials=None, adapt=True):
		credentials = self._credentials_to_use(credentials)
		collection, _ = self._get_collection(credentials=credentials)
		
		link = collection.get_link('UGDSearch')
		url = _check_url(urljoin(self.endpoint, link.href)) + query
		
		rp, data, encoding = do_get(url, credentials, False)
		check_that(rp.status_code == 200, 'invalid status code while searching user data', url, rp.status_code)
		
		data = json.loads(data, encoding=encoding)
		return adapt_ds_object(data) if adapt else data
	
	searchUserContent = search_user_content
	
	def get_user_object(self, user=None, credentials=None, adapt=True):
		credentials = self._credentials_to_use(credentials)
		user = user or credentials[0]
		data = self.execute_user_search(user, credentials, adapt)
		return data['Items'][0] if 'Items' in data and data['Items'] else data
	
	getUserObject = get_user_object
	
	def execute_user_search(self, search, credentials=None, adapt=True):
		
		credentials = self._credentials_to_use(credentials)
		link, _ = self. _get_user_search_link(credentials=credentials)
		url = _check_url(urljoin(self.endpoint, link.href)) + search
		
		rp, data, encoding = do_get(url, credentials, False)
		if rp.status_code == 404:
			return EMPTY_CONTAINER_ARRAY
		
		check_that(rp.status_code == 200, 'invalid status code while getting user object(s)', url, rp.status_code)
		
		data = json.loads(data, encoding=encoding)		
		return adapt_ds_object(data) if adapt else data
		
	executeUserSearch = execute_user_search
	
	def _get_user_search_link(self, credentials=None):
		
		credentials = self._credentials_to_use(credentials)
		ds_ws = self._get_or_parse_user_doc(credentials)
		check_that(ds_ws, "could not find service document for '%s'" % credentials[0], credentials)
		
		ws = ds_ws.get('Global', None)
		check_that(ws, "could not find Global workspace for '%s'" % credentials[0], credentials)
		
		link = ws.get_link('UserSearch')
		check_that(ws, "could not find a UserSearch link in Global workspace for '%s'" % credentials[0], credentials)
		
		return (link, ws)
	
	# --------------
	
	def create_provider(self, name, credentials=None):
		credentials = self._credentials_to_use(credentials)
		provider = Provider(name=name)
		return provider
		
	def create_class(self, classinfo, provider, credentials=None, adapt=True):
		credentials = self._credentials_to_use(credentials)
		collection, _ = self._get_collection(name=provider, workspace='providers', credentials=credentials)
		result = self._post_to_collection(classinfo, collection, credentials, adapt=adapt)
		return result
		
	def get_class(self, provider, class_name, credentials=None, adapt=True):
		credentials = self._credentials_to_use(credentials)
		class_info = self._get_container(class_name, name=provider, workspace='providers', credentials=credentials)
		return adapt_ds_object(class_info) if isinstance(class_info, dict) and adapt else class_info
		
	def add_class_resource(self, resource, provider, class_name, section_name=None, credentials=None, adapt=True):
		credentials = self._credentials_to_use(credentials)
		class_info = self.get_class(provider, class_name, credentials=credentials, adapt=True)
		return class_info
		
	# --------------
	
	def get_user_workspace(self, credentials=None):
		ds_ws = self._get_or_parse_user_doc(credentials)
		return ds_ws.get(credentials[0], None)
	
	def get_collection_data(self, name='Pages', workspace=None, credentials=None, validate=False):
		collection, ws = self._get_collection(name, workspace, credentials, validate)
		collection = self._parse_collection_data(collection.href, credentials) if ws and collection else None
		if ws and collection:
			ws.add_collection(collection)
		return collection
		
	def object_to_persist(self, obj):
		if hasattr(obj, 'toDataServerObject'):
			obj = obj.toDataServerObject()
		result = json.dumps(obj)
		return result
	
	# --------------
	
	def _get_collection(self, name='Pages', workspace=None, credentials=None, validate=True):
		
		credentials = self._credentials_to_use(credentials)
		workspace = workspace or credentials[0]
		ds_ws = self._get_or_parse_user_doc(credentials)
		if validate:
			check_that(ds_ws, "could not find service document for '%s'" % credentials[0], credentials)
		
		ws = ds_ws.get(workspace, None) if ds_ws else None
		if validate:
			check_that(ws, "could not find '%s' workspace" % workspace, workspace)
		
		collection = ws.get_collection(name) if ws else None
		if validate:
			check_that(collection, "could not find '%s' collection" % name, name)
	
		return (collection, ws)
		
	def _get_container(self, container, name='Pages', workspace=None, credentials=None, validate=True):
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
											 credentials=credentials, validate=validate)
		if not collection.has_item(container):
			collection = self.get_collection_data(name=name, workspace=workspace,
												  credentials=credentials, validate=validate)
		
		item = collection.get_item(container)
		return item
	
	def _get_container_raw_item_data(self, container, link_rel, name='Pages', workspace=None, credentials=None, validate=True):
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
			check_that(link, "could not find '%s' link", link_rel)
		elif not link:
			return EMPTY_CONTAINER_DICT
		
		url = urljoin(self.endpoint, link.href)
		rp, data, encoding = do_get(url, credentials, False)
		
		# check for empty reply from the server
		if rp.status_code == 404:
			return EMPTY_CONTAINER_DICT
		
		check_that(rp.status_code == 200, "invalid status code getting '%s'" % link_rel, link_rel, rp.status_code)
		
		data = json.loads(data, encoding=encoding)
		return data
		
	def _post_to_collection(self, obj, collection, credentials=None, adapt=True):
		auth = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, collection.href)
		rp = requests.post(url, auth=auth, data=self.object_to_persist(obj))
		check_that(rp.status_code == 201, 'invalid status code while posting an object', obj, rp.status_code)
		posted = json.loads(rp.content, encoding=get_encoding(rp))
		return adapt_ds_object(posted) if adapt else posted
	
	def _post_raw_content(self, href, source, content_type, slug=None, credentials=None, adapt=True):
		
		auth = self._credentials_to_use(credentials)
		
		if hasattr(source, "read"):
			data = source
		else:
			data = BytesIO()
			data.write(source)
			data.flush()
			data.seek(0)
			
		headers = {'content-type': content_type}
		if slug: headers['slug'] = slug
		
		files = { slug or 'unknown' : data}
		url = urljoin(self.endpoint, href)
		rp = requests.post(url, auth=auth, files=files, headers=headers)
		check_that(rp.status_code == 201, 'invalid status code while posting raw content', href, rp.status_code)
		
		posted = json.loads(rp.content, encoding=get_encoding(rp))
		return adapt_ds_object(posted) if adapt else posted
	
	def _get_or_parse_user_doc(self, credentials=None):
		credentials = self._credentials_to_use(credentials)
		if credentials[0] not in self.users_ws:
			ds = get_user_workspaces(self.endpoint, credentials[0], credentials[1])
			self.users_ws[credentials[0]] = ds
		return self.users_ws[credentials[0]]
		
	def _parse_collection_data(self, href, credentials=None):
		credentials = self._credentials_to_use(credentials)
		url = urljoin(self.endpoint, href)
		rp, data, encoding = do_get(url, credentials, False)
		check_that(rp.status_code == 200, 'invalid status code while getting collection data', href, rp.status_code)
		data = json.loads(data, encoding=encoding)
		return Collection.new_from_dict(data) if data else None
	
	def _credentials_to_use(self, credentials):
		return credentials or self.credentials
	
	# --------------
	
	# abstract away waiting.  Right now we just wait the max
	# time but it will most certainly change.
	# Some things still take longer than we were waiting
	def wait_for_event(self, event=None, max_wait_seconds=3):
		if 'DATASERVER_SYNC_CHANGES' in os.environ:
			# In this case, there should be no need to wait.
			# To help ensure against race conditions on our side,
			# we mimic the old behaviour and wait briefly.
			time.sleep( 0.2 )
			return
		
		if max_wait_seconds and max_wait_seconds > 0:
			time.sleep(max_wait_seconds)
		
	# --------------
	
	createCanvas = create_canvas
	updateObject = update_object
	waitForEvent = wait_for_event
	unshareObject = unshare_object
	setCredentials = set_credentials
	createHighlight = create_highlight
	getFriendsLists = get_friends_lists
	objectToPersist = object_to_persist
	clearCredentials = clear_credentials
	createFriendsList = create_friends_list
	createTextAndBody = create_text_and_body
		
# -----------------------------------

if __name__ == '__main__':
	end_point = 'http://localhost:8081/dataserver2'
	cl = DataserverClient(end_point)
	cl.set_credentials(user='test.user.1@nextthought.com', password='temp001')

	