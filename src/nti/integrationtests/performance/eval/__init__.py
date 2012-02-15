import os
import random

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

def init_server(context):
	port = int(getattr(context, "port", get_open_port()))
	root_dir = os.path.expanduser(getattr(context, "root_dir", '/tmp'))
	use_coverage = getattr(context, "use_coverage", 'False') == 'True'
	
	ds = DataserverProcess(port=port, root_dir=root_dir)
	context.__ds__ = ds
	context.endpoint = ds.endpoint
	
	if not use_coverage:
		ds.start_server()
	else:
		ds.start_server_with_coverage()

def stop_server(context):
	ds = getattr(context, "__ds__", None)
	use_coverage = getattr(context, "use_coverage", 'False') == 'True'
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