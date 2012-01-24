import uuid
import unittest
import collections

from server import DataserverProcess
from server import DEFAULT_USER_PASSWORD
from client import DataserverClient
from client import ROOT_ITEM

class DataServerTestCase(unittest.TestCase):

	user_names = []
	root_item = ROOT_ITEM
	default_user_password = DEFAULT_USER_PASSWORD
	
	# We need to start a dataserver (and stop it)
	# if there is not already one running
	@classmethod
	def setUpClass(cls):
		cls.start_server()
		cls.create_users()

	@classmethod
	def tearDownClass(cls):
		cls.process.terminateServer()

	def setUp(self):
		endpoint = self.get_endpoint()
		self.ds = DataserverClient(endpoint)
		
	@property
	def client(self):
		return self.ds
	
	def get_endpoint(self):
		return getattr(self, 'endpoint', DataserverProcess.ENDPOINT2)
	
	@classmethod
	def new_client(cls, credentials=None, endpoint=None):
		clt = DataserverClient(endpoint or DataserverProcess.ENDPOINT2)
		if credentials:
			clt.set_credentials(credentials)
		return clt
	
	# ======================
	
	@classmethod
	def start_server(cls):
		cls.process = DataserverProcess()
		cls.process.startServer()
		
	@classmethod
	def create_users(cls, max_users=10, create_friends_lists=True):		
		ds = cls.new_client()
		for x in range(1, max_users):
			name = 'test.user.%s@nextthought.com' % x
			cred = (name, DEFAULT_USER_PASSWORD)
			ds.get_user_generated_data('autocreate', credentials=cred)


	