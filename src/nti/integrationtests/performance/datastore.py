import transaction
from threading import local

from ZODB import DB
from ZODB import FileStorage
from BTrees.OOBTree import OOBTree
#from persistent.mapping import PersistentMapping

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
	
	def close(self):
		self.db.close()

if __name__ == '__main__':
	ds = DataStore("/tmp/test.fs")
	ds.close()