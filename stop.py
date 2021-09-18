'''
Fourni les informations sur les arrêts
'''

from libs import get_data_from_json, hms2seconds
from time import time
from urllib.parse import quote
from re import search

search_stop_url = 'https://ws.infotbm.com/ws/1.0/get-schedule/%s'
stop_info_url = 'https://ws.infotbm.com/ws/1.0/network/stoparea-informations/%s'
stop_schedule_url = 'https://ws.infotbm.com/ws/1.0/get-realtime-pass/%d/%s'

line_types = (
	'Tram',
	'Corol',
	'Lianes',
	'Ligne',
	'Bus Relais',
	'Citéis',
)
line_translate = {
	'Tram A': 'A',
	'Tram B': 'B',
	'Tram C': 'C',
	'Tram D': 'D',
	'TBNight': '58',
	'BAT3': '69',
}


def search_stop_by_name (keyword):
	'''
	Recherche la référence d'un nom d'arrêt
	
	Format des données retournées par le site
	[
		{
			id: str, nommé ref par la suite
			name: str
			type: str, mais je ne gère que "stop_area"
			city: str
		},
	]
	'''
	d = get_data_from_json (search_stop_url % quote (keyword))
	r = []
	for i in d:
		if i ['type'] == 'stop_area':
			r.append ({
				'name': i ['name'],
				'city': i ['city'],
				'ref': i ['id'],
			})
	return (r)


def show_stops_from_ref (ref):
	'''
	Affiche la liste des arrêts d'une référence donnée par search_stop_name
	
	Format des données retournées par le site
	{
		id: str, contenu de la variable ref donnée
		name: str
		latitude: str, convertible en float
		longitude: str, convertible en float
		city: str
		hasWheelchairBoarding: bool, accessibilité en fauteuil roulant
		stopPoints: [
			id: str
			name: str, encore le nom
			routes: [
				{
					id: str
					name: str, nom du terminus
					line: {
						name: str, nom pour les humains
					}
				}
			]
		]
	}
	'''
	d = get_data_from_json (stop_info_url % quote (ref))
	r = {
		'ref': d ['id'],
		'name': d ['name'],
		'latitude': float (d ['latitude']),
		'longitude': float (d ['longitude']),
		'city': d ['city'],
		'stop_points': [],
	}
	for i in d ['stopPoints']:
		s = {
			'name': i ['name'],
			'routes': [],
		}
		s ['id'] = int (search ('[0-9]+$', i ['id']).group ())
		for j in i ['routes']:
			rte = {
				'terminus': j ['name'],
				'line_human': j ['line'] ['name'],
			}
			add = False
			if rte ['line_human'] in line_translate:
				line_id = line_translate [rte ['line_human']]
				add = True
			else:
				try:
					line_id = search ('[0-9]+$', rte ['line_human']).group ()
				except AttributeError:
					continue
				line_id = '%02d' % int (line_id)
				for i in line_types:
					if rte ['line_human'] [0:len (i)] == i:
						add = True
						break
			if add:
				rte ['line_id'] = line_id
				s ['routes'].append (rte)
		if s ['routes'] != []:
			r ['stop_points'].append (s)
	return (r)


class StopRoute ():
	'''
	Récupère les informations sur un arrêt
	
	Format des données retournées pas le site
	{
		destinations: {
			<destination_stop_id>: [
				{
					destination_name: str
					realtime: 1 si suivi, 0 sinon
					vehicle_id: str
					vehicle_lattitude: float
					vehicle_longitude: float
					waittime: HH:MM:SS
					waittime_text: str, lisible pas un humain
				},
			]
		}
	}
	'''
	
	def __init__ (self, number, line, autoupdate_at_creation = True, autoupdate = False, autoupdate_delay = -1):
		self.number = number
		self.line = line
		self.last_update = 0
		self.data = None
		if autoupdate_at_creation:
			self.update ()
	
	def update (self, auto = False):
		'''
		Met à jour les données
		'''
		d = get_data_from_json (stop_schedule_url % (self.number, self.line))
		if 'destinations' in d:
			d = d ['destinations']
		else:
			return ()
		self.last_update = time ()
		if type (d) == dict:
			self.data = []
			# let's simplify the data
			for i in d:
				for j in d [i]:
					loc = None
					try:
						loc = (float (j ['vehicle_lattitude']), float (j ['vehicle_longitude']))
					except TypeError:
						pass
					vehicle = {
						'id': j ['vehicle_id'],
						'destination': j ['destination_name'],
						'realtime': j ['realtime'] == '1',
						'location': loc,
						'wait_time': hms2seconds (j ['waittime']),
						'wait_time_human': j ['waittime_text'],
						'arrival': int (self.last_update + hms2seconds (j ['waittime'])),
					}
					self.data.append (vehicle)
			self.data = sorted (self.data, key = lambda item: item ['arrival'])
		else:
			self.last_update = 0
	
	def data_age (self):
		'''
		Retourne l'âge des données
		'''
		return (time () - self.last_update)
	
	def get_line (self):
		class Line ():
			'''
			Information sur la ligne déservie à un arrêt
			'''
			def __init__ (self, data):
				self.ve = data
			
			def vehicles (self):
				if self.ve is not None:
					return (list (range (0, len (self.ve))))
				return ([])
			
			def get_vehicle (self, vehicle):
				class Vehicle ():
					'''
					Information sur un passage de véhicule
					'''
					def __init__ (self, data):
						self.id = data ['id']
						self.location = data ['location']
						self.destination = data ['destination']
						self.is_realtime = data ['realtime']
						self.wait_time = data ['wait_time']
						self.wait_time_text = data ['wait_time_human']
						self.arrival = data ['arrival']
				
				return (Vehicle (self.ve [vehicle]))
		
		return (Line (self.data))
	

if __name__ == '__main__':
	from datetime import datetime
	for word in ('Gravière', 'Gare Saint Jean', 'Quinconces', 'Zorbut'):
		print (word + ':')
		for area in search_stop_by_name (word):
			print ('\t' + area ['name'] + ' (' + area ['city'] + '):')
			for stop in show_stops_from_ref (area ['ref']) ['stop_points']:
				print ('\t\t' + stop ['name'] + ' (' + str (stop ['id']) + '):')
				for route in stop ['routes']:
					print ('\t\t\t' + route ['line_human'] + ' terminus ' + route ['terminus'] + ':')
					sr = StopRoute (stop ['id'], route ['line_id'])
					line = sr.get_line ()
					for vehicle in line.vehicles ():
						v = line.get_vehicle (vehicle)
						if v.is_realtime:
							print ('\t\t\t\t' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)
						else:
							print ('\t\t\t\t~' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)