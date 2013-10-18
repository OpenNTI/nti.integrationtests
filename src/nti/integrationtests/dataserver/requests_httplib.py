#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines requests http wrapper

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

import requests

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

	def do_get(self, url, credentials=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.get(url, headers=headers, params=kwargs, timeout=timeout)
		return rp

	def do_post(self, url, credentials=None, data=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.post(url, data=data, headers=headers, timeout=timeout)
		return rp

	def do_put(self, url, credentials, data=None, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.put(url, data=data, headers=headers, timeout=timeout)
		return rp

	def do_delete(self, url, credentials, **kwargs):
		headers = kwargs.pop('headers', {})
		timeout = kwargs.pop('timeout', 30)
		s = self._get_session(credentials)
		rp = s.delete(url, headers=headers, timeout=timeout)
		return rp
