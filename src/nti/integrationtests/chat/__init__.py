from __future__ import print_function, unicode_literals

import random

from nti.integrationtests.dataserver.server import (SERVER_HOST, PORT)

SOCKET_IO_HOST = SERVER_HOST
SOCKET_IO_PORT = PORT

phrases = (	b'Yellow brown',
			b'Blue red green render purple?',
			b'Alpha beta',
			b'Gamma delta epsilon omega.',
			b'Ash Cat',
			b'Three rendered four five.',
			b'Scathing Moon',
			b'Every red town.',
			b'Yellow uptown',
			b'Interest rendering outer photo!',
			b'Chop Cleanly',
			b'Chicken hacker'
			b'Shoot To Kill',
			b'Bloom, Split and Deviate',
			b'Rankle the Seas and the Skies',
			b'Lightning Flash Flame Shell',
			b'Flower Wind Rage and Flower God Roar, Heavenly Wind Rage and Heavenly Demon Sneer',
			b'All Waves, Rise now and Become my Shield, Lightning, Strike now and Become my Blade',
			b'Cry, Raise Your Head, Rain Without end.',
			b'Sting All Enemies To Death',
			b'Reduce All Creation to Ash',
			b'Sit Upon the Frozen Heavens',
			b'Call forth the Twilight',
			b'Sprint Dust, Call and Rise',
			b'Flute of the Falling Tiger',
			b'Shiver in Fear',
			b'Heaven Chain Slaying Moon',
			b'Heavenly Punishment',
			b'Crest Demon Light',
			b'Faded Scarlet Late Autumn Shower',
			b'Rain Without End',
			b'Truth of Pisces',
			b'Flower Heaven, Crazy Bone',
			b'Crimson Princess',
			b'Splitting Crow',
			b'Flap Away',
			b'Shatter, Collapse, Whisper',
			b'Flying Plum Tree',
			b'Iron Fist Earth-Severing Wind',
			b'Shine Brightly',
			b'Thousand Cherry Blossoms')

def generate_message(k=3, phrases=phrases):
	return ' '.join(random.sample(phrases, k))
