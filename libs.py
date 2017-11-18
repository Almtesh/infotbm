'''
Common libraries
'''

from json import loads as read_json
from urllib import request
from urllib.error import HTTPError

def get_data_from_json (url):
	'''
	gets data from json at url
	'''
	opener = request.build_opener ()
	try:
		return (read_json (opener.open (url).read ().decode ('utf8')))
	except HTTPError:
		return (None)