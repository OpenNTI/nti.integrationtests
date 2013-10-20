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
from urlparse import urljoin

from zope.proxy import ProxyBase

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

class _ResponseProxy(ProxyBase):

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

	def do_session_close(self, s):
		s.close()

	def do_close(self):
		for s in self.sessions.values():
			self.do_session_close(s)
		self.sessions.clear()

class DSRequestHttpLib(RequestHttpLib):

	def __init__(self, endpoint):
		super(DSRequestHttpLib, self).__init__()
		self.endpoint = endpoint

	@classmethod
	def _get_link(cls, response, name):
		try:
			data = response.json()
			links = data.get('Links', ())
			for link in links:
				if link.get('rel') == name:
					return link.get(u'href')
		except:
			pass
		return None
		
	def _get_session(self, credentials=None):
		s = super(DSRequestHttpLib, self)._get_session(credentials=credentials)
		if not getattr(s, 'login', None):
			try:
				url = urljoin(self.endpoint, 'logon.handshake')
				r = s.post(url, data={'username':credentials[0]})

				# save logout
				logout = self._get_link(r, 'logon.logout')
				if logout:
					s.logout = urljoin(self.endpoint, logout)

				# set cookie
				nti_pwd = self._get_link(r, 'logon.nti.password')
				if nti_pwd:
					url = urljoin(self.endpoint, nti_pwd)
					s.get(url)
			except:
				pass
			finally:
				setattr(s, 'login', True)
		return s
	
	def do_session_close(self, s):
		logout = getattr(s, 'logout', None)
		if logout:
			try:
				s.get(logout)
			except:
				pass
		s.close()
	
