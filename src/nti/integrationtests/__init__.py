import uuid
import unittest
import collections

from nti.integrationtests.dataserver.server import PORT
from nti.integrationtests.dataserver.server import DATASERVER_DIR
from nti.integrationtests.dataserver.server import get_open_port
from nti.integrationtests.dataserver.server import DataserverProcess
from nti.integrationtests.dataserver.server import DEFAULT_USER_PASSWORD
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.client import ROOT_ITEM

class DataServerTestCase(unittest.TestCase):

	port = PORT
	root_dir = DATASERVER_DIR
	endpoint = DataserverProcess.ENDPOINT2
	
	user_names = []
	root_item = ROOT_ITEM
	
	default_user_password = DEFAULT_USER_PASSWORD
	
	# We need to start a dataserver (and stop it)
	# if there is not already one running
	@classmethod
	def setUpClass(cls):
		cls.start_server()

	@classmethod
	def tearDownClass(cls):
		cls.process.terminate_server()

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
		cls.process = DataserverProcess(port=cls.port, root_dir=cls.root_dir)
		cls.process.start_server()

