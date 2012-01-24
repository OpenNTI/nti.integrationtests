'''
Created on Dec 21, 2011

@author: ltesti
'''

import json
import plistlib
import cStringIO
import os

class FormatFunctionality(object):

	def urlFormat(self, URL, fmt):
		return URL + '?format=' + fmt

	def read(self): pass

	def write(self): pass
	
	def openObj(self, objFileName):
		tf = os.path.dirname(__file__) + '/../objects/' + objFileName
		with open(tf, "r") as f:
			obj = json.loads(f.read())
		return obj
	
	def openResponse(self, responseFileName):
		tf = os.path.dirname(__file__) + '/../expectedresponse/' + responseFileName
		with open(tf, "r") as f:
			obj = json.loads(f.read())
		return obj
	
class NoFormat(FormatFunctionality):

	def formatURL(self, URL):
		return URL

	def write(self, data):
		return json.dumps(data)

	def read(self, request):
		return json.loads(request.read())

class JsonFormat(FormatFunctionality):

	def formatURL(self, URL):
		return self.urlFormat(URL, 'json')
	
	def write(self, data):
		return json.dumps(data)

	def read(self, request):
		return json.loads(request.read())
	
class PlistFormat(FormatFunctionality):

	def formatURL(self, URL):
		return self.urlFormat(URL, 'plist')

	def write(self, data):
		output = cStringIO.StringIO()
		plistlib.writePlist(data, output)
		data = output.getvalue()
		output.close()
		return data

	def read(self, request):
		return plistlib.readPlistFromString(request.read())
	
	
	