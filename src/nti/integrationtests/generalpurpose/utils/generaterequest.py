import urllib2
from datetime import datetime
from wsgiref import handlers
from time import mktime

class ServerRequest(object):

	def get(self, url, username, password):
		request = urllib2.Request(url=url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		return urllib2.urlopen(request)

	def delete(self, url, username, password):
		request = urllib2.Request(url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		request.get_method = lambda: 'DELETE'
		return urllib2.urlopen(request)

	def put(self, url, data, username, password):
		request = urllib2.Request(url, data)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		request.get_method = lambda: 'PUT'
		return urllib2.urlopen(request)

	def post(self, url, username, password, data):
		request = urllib2.Request(url, data)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		return urllib2.urlopen(request)

	def ifModifiedSinceYes(self, url, username, password):
		request = urllib2.Request(url)
		now = datetime.now()
		stamp = mktime(now.timetuple())
		stamp -= 1000
		GMTTime = handlers.format_date_time(stamp)
		request.headers['If-Modified-Since'] = GMTTime
		try:
			result = urllib2.urlopen(request)
			result.close()
			return result.code
		except urllib2.HTTPError, error:
			return error.code
	
	def ifModifiedSinceNo(self, url, username, password):
		request = urllib2.Request(url=url)
		auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
		auth.add_password(None, url, username, password)
		authendicated = urllib2.HTTPBasicAuthHandler(auth)
		opener = urllib2.build_opener(authendicated)
		urllib2.install_opener(opener)
		response = urllib2.urlopen(request)
		request.add_header('If-Modified-Since', response.headers.get('Last-Modified'))
		try:
			result = urllib2.urlopen(request)
			result.close()
			return result.code
		except urllib2.HTTPError, error:
			return error.code