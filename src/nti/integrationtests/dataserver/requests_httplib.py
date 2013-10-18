#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import sys
import requests
import functools

from zope.proxy import PyProxyBase

def _http_error_logging(f):

	@functools.wraps(f)
	def to_call(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except requests.exceptions.HTTPError, http:
			response = getattr(http, 'response', None)
			_, _, tb = sys.exc_info()

			message = http.message
			message += ' URL: ' + getattr(response, 'url', u'')

			body = getattr(response, 'content', u'')
			message += ' Body: ' + str(body)[-1600:]
			message += '\n Args: ' + str(args)
			message += '\n KWArgs: ' + str(kwargs)

			raise http.__class__(message, response=response), None, tb

		except requests.exceptions.RequestException, http:

			_, _, tb = sys.exc_info()

			message = http.message
			message += '\n Args: ' + str(args)
			message += '\n KWArgs: ' + str(kwargs)

			raise http.__class__(message), None, tb

	return to_call

class _ResponseProxy(PyProxyBase):

	@property
	def code(self):
		return self.status_code

	def read(self):
		return self.content

class RequestHttpLib(object):

	def __init__(self):
		self.sessions = {}

	def _get_session(self, credentials=None):
		result = self.sessions.get(credentials)
		if result is None:
			result = self.sessions[credentials] = requests.Session()
			result.auth = credentials
		return result

	def get_headers(self, rp):
		result = rp.headers
		return result
	
	def body(self, rp):
		result = rp.content
		return result
	
	def deserialize(self, rp):
		result = rp.json()
		return result

	@_http_error_logging
	def do_get(self, url, credentials=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.get(url, headers=headers, params=kwargs, timeout=timeout)
		return _ResponseProxy(rp)

	@_http_error_logging
	def do_post(self, url, credentials=None, data=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.post(url, data=data, headers=headers, timeout=timeout)
		return _ResponseProxy(rp)

	@_http_error_logging
	def do_put(self, url, credentials, data=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.put(url, data=data, headers=headers, timeout=timeout)
		return _ResponseProxy(rp)

	@_http_error_logging
	def do_delete(self, url, credentials, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.delete(url, headers=headers, timeout=timeout)
		return _ResponseProxy(rp)

	def do_close(self):
		for s in self.sessions.values():
			s.close()
		self.sessions.clear()
