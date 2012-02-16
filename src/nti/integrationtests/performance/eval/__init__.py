import os
import random
import tempfile

from nti.integrationtests import generate_ntiid
from nti.integrationtests.dataserver.client import DataserverClient
from nti.integrationtests.dataserver.server import get_open_port
from nti.integrationtests.dataserver.server import DataserverProcess

phrases = (	"Shoot To Kill",
			"Bloom, Split and Deviate",
			"Rankle the Seas and the Skies",
			"Lightning Flash Flame Shell",
			"Flower Wind Rage and Flower God Roar, Heavenly Wind Rage and Heavenly Demon Sneer",
			"All Waves, Rise now and Become my Shield, Lightning, Strike now and Become my Blade", 
			"Cry, Raise Your Head, Rain Without end.",
			"Sting All Enemies To Death",
			"Reduce All Creation to Ash",
			"Sit Upon the Frozen Heavens", 
			"Call forth the Twilight")

boolean_states = {	'1': True, 'yes': True, 'true': True, 'on': True,
					'0': False, 'no': False, 'false': False, 'off': False}

def init_server(context):
	port = int(getattr(context, "port", get_open_port()))
	
	tmp_dir = tempfile.mktemp(prefix="ds.data.", dir="/tmp")
	root_dir = os.path.expanduser(getattr(context, "root_dir", tmp_dir))
	
	use_coverage = getattr(context, "use_coverage", 'False')
	use_coverage = boolean_states.get(use_coverage.lower(), False)
	
	ds = DataserverProcess(port=port, root_dir=root_dir)
	context.__dataserver__ = ds
	context.endpoint = ds.endpoint
	
	if not use_coverage:
		ds.start_server()
	else:
		ds.start_server_with_coverage()

def stop_server(context):
	ds = getattr(context, "__dataserver__", None)
	use_coverage = getattr(context, "use_coverage", 'False')
	use_coverage = boolean_states.get(use_coverage.lower(), False)
	
	if ds:
		if not use_coverage:
			ds.terminate_server()
		else:
			ds.terminate_server_with_coverage()
			
def new_client(context):
	endpoint = getattr(context, "endpoint")
	credentials = getattr(context, "credentials", None)
	client = DataserverClient(endpoint=endpoint, credentials=credentials)
	return client

def generate_message(a_min=1, a_max=4):
	return " ".join(random.sample(phrases, random.randint(a_min, a_max)))

def generate_random_text(a_max=5):
	word = []
	for _ in xrange(a_max+1):
		word.append(chr(random.randint(ord('a'), ord('z'))))
	return "".join(word)