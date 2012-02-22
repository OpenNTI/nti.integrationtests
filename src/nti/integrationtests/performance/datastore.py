import numbers
import transaction
from threading import local

from ZODB import DB
from ZODB import FileStorage
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList
from persistent.interfaces import IPersistent
from persistent.mapping import PersistentMapping

from nti.integrationtests.performance import Subscriber
from nti.integrationtests.performance import RunnerResult
from nti.integrationtests.performance import DelegateContext

from nti.integrationtests.performance.loader import load_results
from nti.integrationtests.performance.loader import process_record

import logging
logger = logging.getLogger(__name__)

# -----------------------------------

class _NoOpCM(object):	
	
	def __enter__(self):
		pass
		
	def __exit__(self, t, v, tb):
		pass
	
# -----------------------------------

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
	
	@classmethod
	def safe_get(cls):
		return getattr(cls.local,'cm', None)

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

# -----------------------------------

def _get_context_manager(store, use_trx=True):
	return store.dbTrans() if use_trx else _NoOpCM()

def _add_timestamp_stores(store, timestamp, use_trx=True):
	with  _get_context_manager(store, use_trx):
		if timestamp not in store.results:
			store.results[timestamp] = PersistentList()
		
		if timestamp not in store.contexts:
			store.contexts[timestamp] = PersistentMapping()
			
def add_result(store, timestamp, record, use_trx=True):
	if isinstance(record, basestring):
		record = process_record(record)
	assert isinstance(record, RunnerResult)
	
	_add_timestamp_stores(store, timestamp, use_trx)
	
	with _get_context_manager(store, use_trx):	
		external = record.to_external_object()
		result = external.get('result', None)
		
		try:
			if 	result is None or \
				isinstance(result, basestring) or \
				isinstance(result, numbers.Real) or \
				IPersistent.implementedBy(result.__class__):
				
				external['result'] = result
			else:
				external['result'] = repr(result)
		except:
			external['result'] = repr(result)
			
		timers = external.pop('custom_timers')
		p_map = PersistentMapping(external)
		p_map.update(timers)
		store.results[timestamp].append(p_map)

def add_context(store, timestamp, context, use_trx=True):

	assert isinstance(context, DelegateContext)
	
	_add_timestamp_stores(store, timestamp, use_trx)
	
	with _get_context_manager(store, use_trx):
		ts_map = store.contexts[timestamp]
		if context.group_name not in ts_map:
			external = context.to_external_object()
			p_map = PersistentMapping(external)
			ts_map[context.group_name] = p_map
	
def batch_load(store, results_file, timestamp=None, groups=None):

	if groups:
		groups = groups.values() if isinstance(groups, dict) else groups
		for group in groups:
			add_context(store, timestamp, group.context)
			
	def inserter(record):
		add_result(store, timestamp, record, False)
			
	with store.dbTrans():
		load_results(results_file, inserter)
			
# -----------------------------------

class ResultDbWriter(object):
	
	def __init__(self, db_file):
		super(ResultDbWriter, self).__init__()
		self.counter = 0
		self.db_file = db_file
		self.store = DataStore(db_file)
		logger.info("saving results to database '%s'", self.db_file)
		
	def close(self):
		self.store.close()
		
	def __call__(self, timestamp, group, result):
		self.counter = self.counter + 1
		add_context(self.store, timestamp, group.context)
		add_result(self.store, timestamp, result)

class ResultBatchDbLoader(Subscriber, ResultDbWriter):
		
	def __call__(self, timestamp, group, result):
		self.counter = self.counter + 1

	def do_batch_load(self, results_file, timestamp, groups=None):
		try:
			batch_load(self.store, results_file, timestamp, groups)
		except Exception ,e:
			logger.exception(e)
	
