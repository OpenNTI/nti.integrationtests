import random
from servertests.server import DataserverClient

# --------------------------

phrases = (	"Yellow brown", "Blue red green render purple?",
			"Alpha beta", "Gamma delta epsilon omega.",
			"One two", "Three rendered four five.",
			"Quick went", "Every red town.",
			"Yellow uptown",  "Interest rendering outer photo!",
			"Preserving extreme", "Chicken hacker", "Reservation swamps",
			"Burried resource", "Slick contracts", "Starving junk",
			"Hueco mundo", "Artificial Soul", "Awaken in my inner world")

ENDPOINT = 'http://localhost:8080/dataserver'

# --------------------------

def new_client(user=None, password='temp001', endpoint = ENDPOINT):
	clt = DataserverClient(endpoint)
	if user:
		password = password or 'temp001'
		clt.setCredentials((user, password))
	return clt
	
def generate_message(min_length=2, max_length=5):
	return " ".join(random.sample(phrases, random.randint(min_length, max_length)))

def post_note(ds_client, container, message=None):
	message = message or generate_message()
	try:
		note = ds_client.createNote(message, container, adapt=True)
	except:
		note = None
	return note