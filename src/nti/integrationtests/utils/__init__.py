#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import os
import time
import base64
import random
import socket
import numbers
import datetime
import ConfigParser

boolean_states = {	u'1': True, u'yes': True, u'true': True, u'on': True,
					u'0': False, u'no': False, u'false': False, u'off': False}

phrases = (	b'Yellow brown',
			b'Blue red green render purple',
			b'Alpha beta',
			b'Gamma delta epsilon omega',
			b'Ash Cat',
			b'Three rendered four five',
			b'Scathing Moon',
			b'Every red town',
			b'Yellow uptown',
			b'Interest rendering outer photo!',
			b'Chop Cleanly',
			b'Chicken hacker'
			b'Shoot To Kill',
			b'Bloom Split and Deviate',
			b'Rankle the Seas and the Skies',
			b'Lightning Flash Flame',
			b'Flower Wind Rage and Flower God Roar Heavenly Wind Rage and Heavenly Demon Sneer',
			b'All Waves Rise now and Become my Shield Lightning Strike now and Become my Blade',
			b'Cry Raise Your Head, Rain Without end',
			b'Sting All Enemies To Death',
			b'Reduce All Creation to Ash',
			b'Sit Upon the Frozen Heavens',
			b'Call forth the Twilight',
			b'Sprint Dust Call and Rise',
			b'Flute of the Falling Tiger',
			b'Shiver in Fear',
			b'Heaven Chain Slaying Moon',
			b'Heavenly Punishment',
			b'Crest Demon Light',
			b'Faded Scarlet Late Autumn Shower',
			b'Rain Without End',
			b'Truth of Pisces',
			b'Flower Heaven Crazy Bone',
			b'Crimson Princess',
			b'Splitting Crow',
			b'Flap Away',
			b'Shatter Collapse Whisper',
			b'Flying Plum Tree',
			b'Iron Fist Earth-Severing Wind',
			b'Shine Brightly',
			b'Thousand Cherry Blossoms',
			b'Prison Uniform of the Remaining Sun')

DEFAULT_USER_PASSWORD = b'temp001'

PORT = int(os.getenv('PORT', b'8081'))
SERVER_HOST = os.getenv('SERVER_HOST', b'localhost')

def eval_bool(s):
	s = unicode(s).lower()
	return boolean_states.get(s, None)

def generate_message(k=3, phrases=phrases):
	result = ' '.join(random.sample(phrases, k))
	return unicode(result)

def generate_random_text(a_max=5):
	word = []
	for _ in xrange(a_max+1):
		word.append(chr(random.randint(ord('a'), ord('z'))))
	result = "".join(word)
	return unicode(result)

def check_url(url):
	result = url + '/' if url[-1] != '/' else url
	return unicode(result)

def get_open_port():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.bind(("",0))
		s.listen(1)
		return s.getsockname()[1]
	finally:
		s.close()
	
def generate_ntiid(date=None, provider='nti', nttype=None, specific=None):

	def escape_provider( provider ):
		return provider.replace( ' ', '_' ).replace( '-', '_' )

	if not nttype:
		raise ValueError( 'Must supply type' )

	date_seconds = date if isinstance( date, numbers.Real ) and date > 0 else time.time()
	date = datetime.date( *time.gmtime(date_seconds)[0:3] )
	date_string = date.isoformat()

	provider = escape_provider( str(provider) ) + '-'
	specific = '-' + specific if specific else '-' + str(time.clock())

	result = 'tag:nextthought.com,%s:%s%s%s' % (date_string, provider, nttype, specific )
	return unicode(result)

def _get_option(method, section, name, default):
	try:
		return method(section, name)
	except:
		return default
	
def get_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.get, section, name, default)

def get_bool_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=False):
	return _get_option(config.getboolean, section, name, default)

def get_int_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.getint, section, name, default)

def get_float_option(config, section=ConfigParser.DEFAULTSECT, name=None, default=None):
	return _get_option(config.getfloat, section, name, default)

