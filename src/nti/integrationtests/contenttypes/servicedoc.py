import warnings

ROOT_ITEM = u'tag:nextthought.com,2011-10:Root'
EMPTY_CONTAINER_DICT  = { u'Last Modified': 0, u'Items': {}}
EMPTY_CONTAINER_ARRAY = { u'Last Modified': 0, u'Items': []}

class Link(object):
	
	def __init__(self, href, rel, type_=None):
		self.rel = rel
		self.href = href
		self.type = type_
	
	def __str__( self ):
		return self.href

	def __repr__( self ):
		return "(%s, %s, %s)" % (self.href, self.type, self.rel)
	
	@classmethod
	def new_from_dict(cls, data):
		rel = data.get('rel', None)
		href = data.get('href', None)
		type_ = data.get('type', None)
		link = Link(href, rel, type_)
		return link
	
class Item(object):
	def __init__(self, ID, href, links=None):
		self.ID = ID
		self.href = href
		self.links = links or {}
	
	def __str__( self ):
		return self.ID
		
	def __repr__( self ):
		return "(%s, %s)" % (self.ID, self.href)
	
	@property
	def is_root(self):
		return ROOT_ITEM == self.ID
	
	def get_link(self, rel):
		return self.links.get(rel, None)
	
	@classmethod
	def new_from_dict(cls, data):
		ID = data.get('ID', None)
		href = data.get('href', None)
		
		links = {}
		for element in data.get('Links', []):
			if not isinstance(element, dict): 
				warnings.warn("Expected a dictionary when parsing a link for a collection item. (%s)" % element)
				continue
			link = Link.new_from_dict(element)
			links[link.rel] = link
			
		item = Item(ID, href, links)
		return item
	
class Collection(object):
	
	def __init__(self, title, href, accepts=[], links=None, items=None):
		self.href = href
		self.title = title
		self.items = items or {}
		self.links = links or []
		self.accepts = accepts or []

	def __str__( self ):
		return self.title

	def __repr__( self ):
		return "(%s, %s, %s, %s)" % (self.title, self.href, self.accepts, self.links)
	
	def get_link(self, rel=None):
		for link in self.links:
			if rel == link.rel:
				return link
		return None
	
	def get_item(self, item_id):
		return self.items.get(item_id, None)
	
	def has_item(self, item_id):
		return item_id in self.items
	
	@classmethod
	def new_from_dict(cls, data):
		href = data['href']
		title = data['Title']
		accepts = data.get('accepts', [])
		
		links = []
		for element in data.get('Links', []):
			if not isinstance(element, dict): 
				warnings.warn("Expected a dictionary when parsing a link for a collection (%s)" % element)
				continue
			links.append(Link.new_from_dict(element))
			
		items = {}
		for element in data.get('Items', []):
			if not isinstance(element, dict): 
				warnings.warn("Expected a dictionary when parsing an item for a collection item. (%s)" % element)
				continue
			item = Item.new_from_dict(element)
			items[item.ID] = item
			
		collection = Collection(title, href, accepts, links, items)
		return collection
	
class Workspace(object):
	
	def __init__(self, title, collections=None, links=None):
		self.title = title
		self.links = links or {}
		self.collections = collections or {}
	
	def add_collection(self, collection):
		self.collections[collection.title] = collection
		
	def get_collection(self, title):
		return self.collections.get(title, None)
	
	def get_link(self, link_rel):
		return self.links.get(link_rel, None)
	
	def __str__( self ):
		return self.title

	def __repr__( self ):
		return self.__str__()
	
	@classmethod
	def new_from_dict(cls, data):
		links = {}
		collections = {}
		
		items = data.get('Items', [])
		for item in items:
			if isinstance(item, dict) and item.get('Class', None) == 'Collection':
				collection = Collection.new_from_dict(item)
				collections[collection.title] = collection
				
		for item in data.get('Links', []):
			if not isinstance(item, dict): 
				warnings.warn("Expected a dictionary when parsing a link for a workspace (%s)" % item)
				continue
			link = Link.new_from_dict(item)
			links[link.rel] = link
		
		workspace = Workspace(data.get('Title', None), collections, links)
		return workspace
