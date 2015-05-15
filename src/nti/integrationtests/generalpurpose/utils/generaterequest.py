#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import requests
from time import mktime
from wsgiref import handlers
from datetime import datetime

from nti.integrationtests.dataserver import httplib

class ServerRequest(object):

	timeout = 60

	def __init__(self):
		self.http = httplib.RequestHttpLib()

	def get(self, url, username, password):
		credentials = (username, password)
		return self.http.do_get(url, credentials, timeout=self.timeout)

	def delete(self, url, username, password):
		credentials = (username, password)
		return self.http.do_delete(url, credentials, timeout=self.timeout)

	def put(self, url, data, username, password):
		credentials = (username, password)
		return self.http.do_put(url, credentials=credentials, data=data, timeout=self.timeout)

	def post(self, url, username, password, data):
		credentials = (username, password)
		return self.http.do_post(url, credentials=credentials, data=data, timeout=self.timeout)

	def ifModifiedSinceYes(self, url, username, password):
		now = datetime.now()
		credentials = (username, password)
		stamp = mktime(now.timetuple()) - 1000
		GMTTime = handlers.format_date_time(stamp)
		headers = {'If-Modified-Since': GMTTime}
		try:
			result = self.http.do_get(url, credentials, headers=headers, timeout=self.timeout)
			return result.status_code
		except requests.exceptions.HTTPError, http:
			response = getattr(http, 'response', None)
			return getattr(response, 'status_code', None)

	def ifModifiedSinceNo(self, url, username, password):
		credentials = (username, password)
		response = self.http.do_get(url, credentials, timeout=self.timeout)
		headers = {'If-Modified-Since': response.headers.get('Last-Modified')}
		try:
			result = self.http.do_get(url, credentials, headers=headers, timeout=self.timeout)
			return result.status_code
		except requests.exceptions.HTTPError, http:
			response = getattr(http, 'response', None)
			return getattr(response, 'status_code', None)
