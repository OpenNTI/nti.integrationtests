#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import urllib2
from datetime import datetime
from wsgiref import handlers
from time import mktime

from nti.integrationtests.dataserver import url_httplib

class ServerRequest(object):

	timeout = 30

	def get(self, url, username, password):
		request = urllib2.Request(url=url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		return url_httplib.urlopen(request, timeout=self.timeout)

	def delete(self, url, username, password):
		request = urllib2.Request(url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		request.get_method = lambda: 'DELETE'
		return url_httplib.urlopen(request, timeout=self.timeout)

	def put(self, url, data, username, password):
		request = urllib2.Request(url, data)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		request.get_method = lambda: 'PUT'
		return url_httplib.urlopen(request, timeout=self.timeout)

	def post(self, url, username, password, data):
		request = urllib2.Request(url, data)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		return url_httplib.urlopen(request, timeout=self.timeout)

	def ifModifiedSinceYes(self, url, username, password):
		request = urllib2.Request(url)
		now = datetime.now()
		stamp = mktime(now.timetuple())
		stamp -= 1000
		GMTTime = handlers.format_date_time(stamp)
		request.headers['If-Modified-Since'] = GMTTime
		try:
			result = url_httplib.urlopen(request, timeout=self.timeout)
			result.close()
			return result.code
		except urllib2.HTTPError as error:
			return error.code

	def ifModifiedSinceNo(self, url, username, password):
		request = urllib2.Request(url=url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		response = urllib2.urlopen(request, timeout=self.timeout)
		request.add_header('If-Modified-Since', response.headers.get('Last-Modified'))
		try:
			result = url_httplib.urlopen(request, timeout=self.timeout)
			result.close()
			return result.code
		except urllib2.HTTPError as error:
			return error.code
