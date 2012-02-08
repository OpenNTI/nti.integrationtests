import sys
import json
import pprint
import httplib
import urllib2

from webob import Response

class URLHttpLib(object):

    def __init__(self, debug=False):
        self.debug = debug
        
    # -----------------------------------
     
    @classmethod
    def _get_encoding(cls, obj):
        data = None
        
        if isinstance(obj, httplib.HTTPMessage):
            data = obj.headers.dict.get('content-type', None)
        elif isinstance(obj, dict):
            data = obj.get('content-type', None)
        
        data = str(data) if data else 'UTF-8'
        if data.find('charset=') != -1:
            data = data[data.find('charset=') + 8:]
        return data

    @classmethod
    def _create_response(cls, code=None, rp=None):
        status = rp.code if rp else code
        body = rp.read() if rp else u''
        headers = rp.headers.dict if rp else {}
        headerlist = [(k,v) for k,v in headers.items()]
        charset = cls._get_encoding(headers)
        return Response(body=body, status=status, headerlist=headerlist, charset=charset)
    
    @classmethod
    def _http_ise_error_logging(cls, f):
        def to_call( *args, **kwargs ):
            try:
                rp = f( *args, **kwargs )
                return cls._create_response(rp=rp)
            except urllib2.HTTPError as http:
                
                # handle 404s differently
                if http.code == 404:
                    return cls._create_response(code=404)
                
                # If the server sent us anything,
                # try to use it
                _, _, tb = sys.exc_info()
                try:
                    http.msg += ' URL: ' + http.geturl()
                    body = http.read()
                    # The last 20 or so lines
                    http.msg += ' Body: ' + str( body )[-1600:]
                except (AttributeError, IOError):
                    pass
                
                http.msg += '\n Args: ' + str(args)
                http.msg += '\n KWArgs: ' + str(kwargs)
                
                # re-raise the original exception object
                # with the original traceback
                raise http, None, tb
            
        return to_call

    @_http_ise_error_logging
    def _do_request(self, request):
        return urllib2.urlopen(request)

    def _do_debug(self, url, rp, credentials):
        if self.debug:
            raw_content = rp.body
            try:
                dt = json.loads(rp.body, encoding=rp.charset) if raw_content else {}
            except Exception, e:
                dt = {'Exception': e}
            d = {'data':dt, 'url':url, 'auth':credentials, 'raw': raw_content}
            pprint.pprint(d)
            
    # -----------------------------------
    
    def do_get(self, url, credentials, *args, **kwargs):
        request = urllib2.Request(url=url)
        auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth.add_password(None, url, credentials[0], credentials[1])
        authendicated = urllib2.HTTPBasicAuthHandler(auth)
        opener = urllib2.build_opener(authendicated)
        urllib2.install_opener(opener)
        rp = self._do_request(request)
        self._do_debug(url, rp, credentials)
        return rp

    def do_post(self, url, credentials, data, *args, **kwargs):
        request = urllib2.Request(url, data)
        auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth.add_password(None, url, credentials[0], credentials[1])
        authendicated = urllib2.HTTPBasicAuthHandler(auth)
        opener = urllib2.build_opener(authendicated)
        urllib2.install_opener(opener)
        rp = self._do_request(request)
        self._do_debug(url, rp, credentials)
        return rp

    def do_put(self, url, credentials, data, *args, **kwargs):
        request = urllib2.Request(url, data)
        auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth.add_password(None, url, credentials[0], credentials[1])
        authendicated = urllib2.HTTPBasicAuthHandler(auth)
        opener = urllib2.build_opener(authendicated)
        urllib2.install_opener(opener)
        request.get_method = lambda: 'PUT'
        rp = self._do_request(request)
        self._do_debug(url, rp, credentials)
        return rp

    def do_delete(self, url, credentials, *args, **kwargs):
        request = urllib2.Request(url)
        auth = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth.add_password(None, url, credentials[0], credentials[1])
        authendicated = urllib2.HTTPBasicAuthHandler(auth)
        opener = urllib2.build_opener(authendicated)
        urllib2.install_opener(opener)
        request.get_method = lambda: 'DELETE'
        rp = self._do_request(request)
        self._do_debug(url, rp, credentials)
        return rp
