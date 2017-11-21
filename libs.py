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

def hms2seconds (hhmmss):
	'''
	Convert H:M:S string to time in seconds
	'''
	try:
		cut_string = hhmmss.split (':')
		cut_time = (int (cut_string [0]), int (cut_string [1]), int (cut_string [2]))
		return (3600 * cut_time [0] + 60 * cut_time [1] + cut_time [2])
	except:
		return (0)