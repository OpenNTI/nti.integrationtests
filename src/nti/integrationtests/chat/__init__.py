import random

from nti.integrationtests.dataserver.server import (SERVER_HOST, PORT)

SOCKET_IO_HOST = SERVER_HOST
SOCKET_IO_PORT = PORT

phrases = (	u'Yellow brown',
			u'Blue red green render purple?',
			u'Alpha beta',
			u'Gamma delta epsilon omega.',
			u'Ash Cat',
			u'Three rendered four five.',
			u'Scathing Moon',
			u'Every red town.',
			u'Yellow uptown',
			u'Interest rendering outer photo!',
			u'Chop Cleanly',
			u'Chicken hacker'
			u'Shoot To Kill',
			u'Bloom, Split and Deviate',
			u'Rankle the Seas and the Skies',
			u'Lightning Flash Flame Shell',
			u'Flower Wind Rage and Flower God Roar, Heavenly Wind Rage and Heavenly Demon Sneer',
			u'All Waves, Rise now and Become my Shield, Lightning, Strike now and Become my Blade',
			u'Cry, Raise Your Head, Rain Without end.',
			u'Sting All Enemies To Death',
			u'Reduce All Creation to Ash',
			u'Sit Upon the Frozen Heavens',
			u'Call forth the Twilight',
			u'Sprint Dust, Call and Rise',
			u'Flute of the Falling Tiger',
			u'Shiver in Fear',
			u'Heaven Chain Slaying Moon',
			u'Heavenly Punishment',
			u'Crest Demon Light',
			u'Faded Scarlet Late Autumn Shower',
			u'Rain Without End',
			u'Truth of Pisces',
			u'Flower Heaven, Crazy Bone',
			u'Crimson Princess',
			u'Splitting Crow',
			u'Flap Away',
			u'Shatter, Collapse, Whisper',
			u'Flying Plum Tree',
			u'Iron Fist Earth-Severing Wind',
			u'Shine Brightly',
			u'Thousand Cherry Blossoms')

def generate_message(k=3, phrases=phrases):
	return ' '.join(random.sample(phrases, k))
