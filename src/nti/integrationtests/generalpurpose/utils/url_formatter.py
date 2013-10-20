#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import anyjson
import plistlib
import cStringIO

def _content(response):
	if hasattr(response, 'read'):
		result = response.read()
	elif hasattr(response, 'content'):
		result = response.content
	else:
		result = u''
	return result

class FormatFunctionality(object):

	def urlFormat(self, URL, fmt):
		return URL + '?format=' + fmt

	def read(self):
		pass

	def write(self):
		pass
	
class NoFormat(FormatFunctionality):

	def formatURL(self, URL):
		return URL

	def write(self, data):
		return anyjson.dumps(data)

	def read(self, response):
		return anyjson.loads(_content(response))

class JsonFormat(FormatFunctionality):

	def formatURL(self, URL):
		return self.urlFormat(URL, 'json')
	
	def write(self, data):
		return anyjson.dumps(data)

	def read(self, response):
		return anyjson.loads(_content(response))
	
class PlistFormat(FormatFunctionality):

	def formatURL(self, URL):
		return self.urlFormat(URL, 'plist')

	def write(self, data):
		output = cStringIO.StringIO()
		plistlib.writePlist(data, output)
		data = output.getvalue()
		output.close()
		return data

	def read(self, response):
		return plistlib.readPlistFromString(_content(response))
