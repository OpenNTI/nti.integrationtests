import transaction
from threading import local

from ZODB import DB
from ZODB import FileStorage
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from nti.integrationtests.performance import RunnerResult
from nti.integrationtests.performance import DelegateContext
from nti.integrationtests.performance.loader import process_record

# =====================

class _ContextManager(object):	
	local = local()
	
	def __init__(self, db):
		self.db = db
		self.tm = None
		self.txn = None
		self.conn = None

	def __enter__(self):
		self.tm = transaction.TransactionManager()
		self.conn = self.db.open( self.tm )
		self.txn = self.tm.begin()
		self.local.cm = self
		return self.conn
		
	def __exit__(self, t, v, tb):
		try:
			if t is None:
				self.tm.commit()
			else:
				self.tm.abort()
			self.tm = None
		finally:
			self.close()
	
	def close(self):
		if self.conn:
			try:
				self.conn.close()
			except: 
				pass
			
		self.tm = None
		self.conn = None
			
		try:
			del self.local.cm
		except:
			pass
		
	def connected(self):
		return self.conn is not None
	
	def abort(self):
		if self.tm:
			self.tm.abort()
			
	def commit(self):
		if self.tm:
			self.tm.commit()
		
	@classmethod
	def get(cls):
		return cls.local.cm

# =====================

class DataStore():
	def __init__(self, path):
		self.path = path
		self.storage = FileStorage.FileStorage(path)
		self.db = DB(self.storage)
		self.check_stores()
			
	def check_stores(self):
		with self.dbTrans() as conn:
			dbroot = conn.root()
			for key in ('results', 'contexts'):
				if not dbroot.has_key(key):
					dbroot[key] = OOBTree()
				
	def dbTrans(self):
		return _ContextManager(self.db)
	
	@property	
	def root(self):
		return _ContextManager.get().conn.root()
	
	@property	
	def results(self):
		return self.root['results']
	
	@property	
	def contexts(self):
		return self.root['contexts']
	
	def close(self):
		self.db.close()

# =====================

def _add_timestamp_stores(store, timestamp):
	with store.dbTrans():
		if timestamp not in store.results:
			store.results[timestamp] = PersistentList()
		
		if timestamp not in store.contexts:
			store.contexts[timestamp] = PersistentMapping()
			
def add_result(store, timestamp, result):
	if isinstance(result, basestring):
		result = process_record(result)
	assert isinstance(result, RunnerResult)
	
	_add_timestamp_stores(store, timestamp)
	with store.dbTrans():	
		external = result.to_external_object()
		timers = external.pop('custom_timers')
		p_map = PersistentMapping(external)
		p_map.update(timers)
		store.results[timestamp].append(p_map)

def add_context(store, timestamp, context):

	assert isinstance(context, DelegateContext)
	
	_add_timestamp_stores(store, timestamp)
	
	with store.dbTrans():
		ts_map = store.contexts[timestamp]
		if context.group_name not in ts_map:
			external = context.to_external_object()
			p_map = PersistentMapping(external)
			ts_map[context.group_name] = p_map
		

class ResultDbWriter(object):
	
	def __init__(self, db_file):
		super(ResultDbWriter, self).__init__()
		self.store = DataStore(db_file)
		self.db_file = db_file
		self.counter = 0
		
	def close(self):
		self.store.close()
		
	def __call__(self, timestamp, group, result):
		self.counter = self.counter + 1
		add_context(self.store, timestamp, group.context)
		add_result(self.store, timestamp, result)

		
if __name__ == '__main__':
	ds = DataStore("/tmp/test.fs")
	ds.close()