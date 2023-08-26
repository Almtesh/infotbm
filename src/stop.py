from utils import get_data_from_json
from urllib.parse import quote
from stop_point import StopPoint
from re import search
from route import Route


INFO_URL = 'https://ws.infotbm.com/ws/1.0/network/stoparea-informations/%s'

LINE_TRANSLATE = {
	'Tram A': 'A',
	'Tram B': 'B',
	'Tram C': 'C',
	'Tram D': 'D',
	'TBNight': '58',
	'BAT3': '69',
}

LINE_TYPES = (
	'Tram',
	'Corol',
	'Lianes',
	'Ligne',
	'Bus Relais',
	'Citéis',
)


class Stop:
	def __init__ (self, id, name, latitude, longitude, city):
		self.id = id
		self.name = name
		self.latitude = latitude
		self.longitude = longitude
		self.city = city
		self.stopPoints = []

	def getId (self):
		return self.id

	def getName (self):
		return self.name

	def getLatitude (self):
		return self.latitude

	def getLongitude (self):

		return self.longitude

	def getCity (self):
		return self.city

	def getStopPoints (self):
		return self.stopPoints

	def setStopPoints (self, stopPoints):
		self.stopPoints = stopPoints

	def __repr__ (self):
		return self.name + ' (' + self.city + ')' + ' (id: ' + self.id + ')'

	def __str__ (self):
		return self.name + ' (' + self.city + ')' + ' (id: ' + self.id + ')'


def get_stop_by_id (id):
	data = get_data_from_json (INFO_URL % quote (id))
	stop = Stop (
		data ['id'],
		data ['name'],
		float (data ['latitude']),
		float (data ['longitude']),
		data ['city'],
	)
	stopPoints = []
	for i in data ['stopPoints']:
		stopPoint = StopPoint (i ['name'])
		routes = []
		stopPoint.setId (int (search ('[0-9]+$', i ['id']).group ()))
		for j in i ['routes']:
			route = Route (j ['id'], j ['name'], j ['line'] ['name'])
			add = False
			if route.getLineName () in LINE_TRANSLATE:
				line_id = LINE_TRANSLATE [route.getLineName ()]
				add = True
			else:
				try:
					line_id = search ('[0-9]+$', route.getLineName ()).group ()
				except AttributeError:
					continue
				line_id = '%02d' % int (line_id)
				for i in LINE_TYPES:
					if route.getLineName () [0:len (i)] == i:
						add = True
						break
			if add:
				route.setId (line_id)
				routes.append (route)
				stopPoint.setRoutes (routes)
		if stopPoint.getRoutes () != []:
			stopPoints.append (stopPoint)
			stop.setStopPoints (stopPoints)
	return stop