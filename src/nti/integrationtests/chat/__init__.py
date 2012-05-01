import random

from nti.integrationtests.dataserver.server import (SERVER_HOST, PORT)

SOCKET_IO_HOST = SERVER_HOST
SOCKET_IO_PORT = PORT

phrases = (	"Yellow brown",
			"Blue red green render purple?",
			"Alpha beta",
			"Gamma delta epsilon omega.",
			"One two",
			"Three rendered four five.",
			"Quick went",
			"Every red town.",
			"Yellow uptown",
			"Interest rendering outer photo!",
			"Preserving extreme",
			"Chicken hacker"
			"Shoot To Kill",
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

def generate_message(a_min=1, a_max=4, phrases=phrases):
	return " ".join(random.sample(phrases, random.randint(a_min, a_max)))
