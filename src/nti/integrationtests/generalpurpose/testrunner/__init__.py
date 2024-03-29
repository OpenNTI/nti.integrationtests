#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import sys
import json
import time
import requests
import functools
from urlparse import urljoin

from nti.integrationtests.generalpurpose.utils.url_formatter import NoFormat
from nti.integrationtests.generalpurpose.utils.generaterequest import ServerRequest

from hamcrest import (assert_that, greater_than_or_equal_to, less_than_or_equal_to, has_entry)

from abc import ABCMeta, abstractmethod

class BasicSeverOperation(object):

	__metaclass__ = ABCMeta

	format = None
	objTest = None
	requests = None
	testArgs = None
	endpoint = None
	username = None
	password = None
	href_url = None
	testObjRef = None
	putObjData = None
	postObjData = None
	objResponse = None
	testHrefUrl = None
	responseCode = None
	testPassword = None
	lastModified = None
	preRequestTime = None
	lastModifiedCollection = None

	# Methods called by the generator should copy this data
	# into their local frame's __traceback_info__ variable
	_traceback_info_ = None

	@abstractmethod
	def makeRequest(self, kwargs ):
		raise NotImplementedError()

	def setValues(self, kwargs):

		self.requests = ServerRequest()
		self.objTest = kwargs['bodyTester']
		self.format  = kwargs.get('format', NoFormat())

		_href = kwargs['href']
		_input_info = kwargs['responseTypes']
		_data = kwargs['objRunner']['objects']

		self.endpoint = kwargs['endpoint']
		self.username = kwargs['username']
		self.password = kwargs['password']
		self.responseCode = kwargs['responseTypes']
		self.testPassword = _input_info.get('password', self.password)

		self.href_url = urljoin(self.endpoint, _href)
		self.putObjData = _data['put_data']
		self.postObjData = _data['post_data']

		self.testObjRef = _input_info.get('id', None)
		self.objResponse = kwargs['objRunner']['expected_return']
		self.testHrefUrl = urljoin(self.endpoint, _input_info.get('href', _href))

		self.testArgs = None
		self.preRequestTime = 0

	def make_quiz_result_request(self, kwargs):
		new_server_request = ServerRequest()
		no_format = NoFormat()
		url = urljoin(kwargs['endpoint'], kwargs['href'])
		data = no_format.write(kwargs['objRunner']['quiz_obj']['post_data'])
		request = new_server_request.post(url=url, data=data, \
									username=kwargs['username'], password=kwargs['password'])
		parsed_body = no_format.read(request)
		kwargs['objRunner']['objects']['post_data']['QuizID'] = parsed_body['ID']
		kwargs['objRunner']['objects']['put_data']['QuizID'] = parsed_body['ID']
		self.makeRequest(kwargs)

	makeQuizResultRequest  = make_quiz_result_request

	def obj_setUp(self):
		if self.testObjRef:
			url = urljoin(self.endpoint, self.testObjRef)
			self.testArgs = {'url_id':url, 'id' : self.testObjRef}
		else:
			url = self.format.formatURL(self.href_url)
			data = self.format.write(self.postObjData)
			request = self.requests.post(url=url, data=data, username=self.username, password=self.password)
			parsed_body = self.format.read(request)

			if parsed_body['href'].find('/Objects/') != -1:
				url = urljoin(self.endpoint, parsed_body['href'])
				self.testArgs = {'url_id':url, 'id' : parsed_body['href']}
			# TODO: The above is an invalid assumption. /objects/ is not always in an href
			# what breaks with the following code?
			elif parsed_body['href']:
				url = urljoin(self.endpoint, parsed_body['href'])
				self.testArgs = {'url_id':url, 'id' : parsed_body['href']}
			else:
				self.testArgs = None
		return self.testArgs

	def obj_tearDown(self, objref=None):
		try:
			url = urljoin(self.endpoint, objref) if objref else self.testArgs['url_id']
			__traceback_info__ = url, objref, self
			self.requests.delete(url=url, username=self.username, password=self.password)
		except requests.exceptions.HTTPError:
			# Normally this will be swallowed. But if we fail later, and logcapture is on
			# this might be handy
			logger.exception( "Failed to delete during cleanup" )

	def set_modification_time(self, parsed_body):
		self.lastModified = parsed_body.get( 'LastModified', parsed_body.get( 'Last Modified' ) )
		return self.lastModified
	setModificationTime = set_modification_time

	def set_collection_modification_time(self):
		try:
			request = self.requests.get(self.href_url, self.username, self.password)
			parsed_body = json.loads(request.read())
			self.lastModifiedCollection = parsed_body['Last Modified']
			return self.lastModifiedCollection
		except (requests.exceptions.HTTPError, KeyError):
			self.lastModifiedCollection = None
	setCollectionModificationTime = set_collection_modification_time

	def set_time(self):
		self.preRequestTime = time.time()
	setTime = set_time

	def check_changed_last_modified_time(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		lastModifiedTime = kwargs.get('requestTime', None)
		preRequestTime = kwargs['preRequestTime']
		if lastModifiedTimeCollection:
			assert_that( kwargs, has_entry( 'collectionTime', greater_than_or_equal_to( preRequestTime ) ) )

		if lastModifiedTime:
			assert_that( kwargs, has_entry( 'requestTime', greater_than_or_equal_to( preRequestTime ) ) )

	changedLastModifiedTime = check_changed_last_modified_time

	def check_unchanged_last_modified_time(self, **kwargs):
		lastModifiedTimeCollection = kwargs.get('collectionTime', None)
		preRequestTime = kwargs['preRequestTime']
		lastModifiedTime = kwargs.get('requestTime', None)
		if lastModifiedTimeCollection and preRequestTime:
			assert_that( kwargs, has_entry( 'collectionTime', less_than_or_equal_to( preRequestTime ) ) )

		if lastModifiedTime and preRequestTime:
			assert_that( kwargs, has_entry( 'requestTime', less_than_or_equal_to( preRequestTime ) ) )


	unchangedLastModifiedTime = check_unchanged_last_modified_time
