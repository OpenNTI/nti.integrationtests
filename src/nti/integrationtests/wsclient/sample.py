'''
Created on Jan 15, 2013

@author: csanchez
'''
import json
import pprint
import requests

WS_BROADCAST = b'5:::'
_LIGHTWEIGHT_FRAME_DELIM      = b'\xff\xfd'     # u'\ufffd', the opening byte of a lightweight framing
_LIGHTWEIGHT_FRAME_UTF8_DELIM = b'\xef\xbf\xbd' # utf-8 encoding of u'\ufffd'

def decode_multi(  data ):
	"""
	:return: A sequence of Message objects
	"""
	DELIM1 = _LIGHTWEIGHT_FRAME_DELIM
	DELIM2 = _LIGHTWEIGHT_FRAME_UTF8_DELIM

	# If they give us a unicode object (weird!)
	# encode as bytes in utf-8 format
	if isinstance( data, unicode ):
		data = data.encode( 'utf-8' )
	assert isinstance( data, str ), "Must be a bytes object, not unicode"

	if not data.startswith( DELIM1 ) and not data.startswith( DELIM2 ):
		# Assume one
		return ( data, )

	d = DELIM1
	dl = 2
	if data.startswith( DELIM2 ):
		d = DELIM2
		dl = 3

	messages = []
	start = 0
	while start + dl < len(data):
		start_search = start + dl
		end = data.find( d, start_search )
		len_str = int( data[start_search:end] )
		if len_str <= 0: raise ValueError( 'Bad length' )
		end_data = end + dl + len_str
		sub_data = data[end+dl:end_data]
		if not sub_data: raise ValueError( "Data from %s to %s was not len %s (got %s)" % (start_search, end_data, len_str, sub_data ) )
		if not len(sub_data) == len_str: raise ValueError( "Data from %s to %s was not len %s (got %s)" % (start_search, end_data, len_str, sub_data ) )
		messages.append( sub_data  )

		start = end_data

	return messages
	
if __name__ == '__main__':
	WS_BROADCAST = b'5:::'
	EVT_ENTER_ROOM	= 'chat_enterRoom'
	EVT_POST_MESSAGE= 'chat_postMessage'
	DEFAULT_CHANNEL = 'DEFAULT'
	
	url = 'http://localhost:8081'
	auth=('carlos.sanchez@nextthought.com', 'carlos.sanchez')
	resource = '/socket.io/1/'
	urlf = url + resource
	r = requests.post(urlf, auth=auth)
	msg = r.text
	print(msg)
	sessiond_id = msg.split(':')[0]
	resource = '%s%s/%s' % (resource, 'xhr-polling', sessiond_id)
	urlf = url + resource
	
	hostport = "localhost:8081"
	headers = {'Origin': hostport, 'Host':hostport}
	r = requests.post(urlf, auth=auth, headers=headers)
	print(r)
	print(r.text)
	
	occupants = (u'carlos.sanchez@nextthought.com', u'troy.daley@nextthought.com')
	containerId = u'tag:nextthought.com,2011-10:AOPS-HTML-prealgebra.why_start_with_arithmetic_'

	args = {u"Occupants": occupants}
	args[u"ContainerId"] = containerId

	d = {u"name":EVT_ENTER_ROOM, u"args":[args]}
	msg = json.dumps(d)
	msg = WS_BROADCAST + msg
	msg = msg.encode("utf-8")
	
	r = requests.post(urlf, auth=auth, data=msg)
	
	r = requests.get(urlf, auth=auth)
	
	msg = decode_multi(r.text)[0]
	msg = msg[len(WS_BROADCAST):]
	
	d = json.loads(msg)
	pprint.pprint(d)
	d = d['args'][0]
	
	roomid = d.get('ID', d.get('id', None))
	print(roomid)
	
	message = u'carlos'
	channel = DEFAULT_CHANNEL
		
	args = {u"ContainerId": roomid, u"Body": message, u"Class":"MessageInfo", u'channel':channel}
	d = {u"name":EVT_POST_MESSAGE, u"args":[args]}
	msg = json.dumps(d)
	msg = WS_BROADCAST + msg
	msg = msg.encode("utf-8")
	
	r = requests.post(urlf, auth=auth, data=msg)
	print(r)
	print(r.text)
	
	r = requests.get(urlf, auth=auth)
	print(r)
	for m in decode_multi(r.text):
		print(m)
	
	r = requests.get(urlf, auth=auth)
	print(r)
	for m in decode_multi(r.text):
		print(m)
		
