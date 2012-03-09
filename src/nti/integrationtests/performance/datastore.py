import numbers
import transaction

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
	
# =====================

class DataStore():
	
	transaction_manager = transaction.TransactionManager()
	
	def __init__(self, path):
		self.path = path
		self.storage = FileStorage.FileStorage(path)
		self.db = DB(self.storage)
		self.conn = self.db.open(self.transaction_manager)
		self.check_stores()
			
	def check_stores(self):
		with self.dbTrans():
			for key in ('results', 'contexts'):
				if not self.root.has_key(key):
					self.root[key] = OOBTree()
				
	def dbTrans(self):
		return self.transaction_manager
	
	@property	
	def root(self):
		return self.conn.root()
	
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
		inserter.counter = inserter.counter + 1
		add_result(store, timestamp, record, False)
	inserter.counter = 0
		
	with store.dbTrans():
		load_results(results_file, inserter)
	
	return inserter.counter

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

class ResultBatchDbLoader(ResultDbWriter, Subscriber):
		
	def __init__(self, db_file, timestamp, groups, results_file):
		super(ResultBatchDbLoader, self).__init__(db_file)
		self.groups = groups
		self.timestamp = timestamp
		self.results_file = results_file
		
	def close(self):
		try:
			self.do_batch_load()
		finally:
			super(ResultBatchDbLoader, self).close()
			
	def __call__(self, timestamp, group, result):
		self.counter = self.counter + 1

	def do_batch_load(self):
		try:
			batch_load(self.store, self.results_file, self.timestamp, self.groups)
		except Exception ,e:
			logger.exception(e)
	
