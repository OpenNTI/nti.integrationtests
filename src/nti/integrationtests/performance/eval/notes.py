from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message

def create_notes():
	context = create_notes.__context__
	client = new_client(context)
	result = client.create_note(generate_message(1,1), container=generate_ntiid(nttype='test'))
	return result

if __name__ == '__main__':
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "notes_config.cfg")
	run(config_file)