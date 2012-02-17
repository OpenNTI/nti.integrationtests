from nti.integrationtests.performance.eval import new_client
from nti.integrationtests.performance.eval import generate_ntiid
from nti.integrationtests.performance.eval import generate_message
from nti.integrationtests.performance.eval import generate_random_text

def create_note():
	context = create_note.__context__
	client = new_client(context)
	nttype = generate_random_text()
	result = client.create_note(generate_message(1,4), container=generate_ntiid(nttype=nttype))
	assert result, 'could  not create note'
	return result

if __name__ == '__main__':
	import os
	from nti.integrationtests.performance.runner import run
	config_file = os.path.join(os.path.dirname(__file__), "notes_config.cfg")
	run(config_file)