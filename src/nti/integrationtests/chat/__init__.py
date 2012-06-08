import random

from nti.integrationtests.dataserver.server import (SERVER_HOST, PORT)

SOCKET_IO_HOST = SERVER_HOST
SOCKET_IO_PORT = PORT

phrases = (	"Yellow brown",
			"Blue red green render purple?",
			"Alpha beta",
			"Gamma delta epsilon omega.",
			"Ash Cat",
			"Three rendered four five.",
			"Scathing Moon",
			"Every red town.",
			"Yellow uptown",
			"Interest rendering outer photo!",
			"Chop Cleanly",
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
			"Call forth the Twilight",
			"Sprint Dust, Call and Rise",
			"Flute of the Falling Tiger",
			'Shiver in Fear',
			'Heaven Chain Slaying Moon',
			'Heavenly Punishment',
			'Crest Demon Light',
			'Faded Scarlet Late Autumn Shower',
			'Rain Without End',
			'Truth of Pisces',
			'Flower Heaven, Crazy Bone',
			'Crimson Princess',
			'Splitting Crow',
			'Flap Away',
			'Shatter, Collapse, Whisper',
			'Flying Plum Tree',
			'Iron Fist Earth-Severing Wind',
			'Shine Brightly',
			'Thousand Cherry Blossoms')

def generate_message(k=3, phrases=phrases):
	return ' '.join(random.sample(phrases, k))
