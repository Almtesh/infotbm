'''
Provides all info from a stop
'''

from libs import get_data_from_json, hms2seconds
from time import time

stop_schedule_url = 'http://plandynamique.infotbm.com/api/schedules?stop=%d'

def get_stop_list ():
	'''
	Gets stop name after its number
	'''
	l = {}
	
	# Trams
	data = get_data_from_json ('http://plandynamique.infotbm.com/api/file/trams.xml')
	for i in data ['arret']:
		num = []
		loc = None
		try:
			loc = (float (i ['x']), float (i ['y']))
		except:
			pass
		if type (i ['ligne']) == dict:
			num.append (int (i ['ligne'] ['StopPointExternalCode'].replace ('TBT', '')))
		else:
			for j in i ['ligne']:
				num.append (int (j ['StopPointExternalCode'].replace ('TBT', '')))
		for j in num:
			l [j] = {'name': i ['nom'], 'location': loc}
	#Bus
	data = get_data_from_json ('http://plandynamique.infotbm.com/api/file/bus.xml')
	for i in data ['arret']:
		n = int (i ['StopPointExternalCode'].replace ('TBC', ''))
		loc = None
		try:
			loc = (float (i ['x']), float (i ['y']))
		except:
			pass
		l [n] = {'name': i ['StopName'], 'location': loc}
	
	return (l)

class Stop ():
	'''
	Gather stop informations
	
	data format as returned by infotbm:
	[
		{
			origin: str, # source de l'information, BDSI tout le temps semble-t-il
			type: str, # type de ligne (Bus, Tramway, Ferry)
			message: str,
			code: str, # nom de la ligne
			name: str, # nom complet de la ligne
			schedules: [
				{
					arrival: str,
					arrival_commande: str,
					arrival_theorique: str,
					comment: str,
					departure: str,
					departure_commande: str,
					departure_theorique: str,
					destination_id: int,
					destination_name: str,
					origin: str,
					realtime: int,
					schedule_id: int,
					trip_id: int,
					updated_at: str, # last data update
					vehicle_id: int,
					vehicle_lattitude: float,
					vehicle_longitude: float,
					vehicle_position_updated_at: str, # last update from vehicle
					waittime: str, # estimated wait time in %H:%M:%S format
					waittime_text: str, # human readable estimated wait time written in French
				},
			],
		}
	]
	'''
	
	def __init__ (self, number, autoupdate_at_creation = True, autoupdate = False, autoupdate_delay = -1):
		self.number = number
		self.last_update = 0
		self.data = None
		if autoupdate_at_creation:
			self.update ()
	
	def update (self, auto = False):
		'''
		Updates data
		auto optionnal param is to set if a update is a automatic one, and must be performed as defined in autoupdate_delay variable
		'''
		d = get_data_from_json (stop_schedule_url % self.number)
		self.last_update = time ()
		if d != False:
			self.data = []
			# let's simplify the data
			for i in d:
				l = {
					'id': i ['code'],
					'name': i ['name'],
					'vehicle_type': i ['type'],
					'vehicles': [],
				}
				for j in i ['schedules']:
					loc = None
					try:
						loc = (float (j ['vehicle_lattitude']), float (j ['vehicle_longitude']))
					except TypeError:
						pass
					l ['vehicles'].append ({
						'id': j ['vehicle_id'],
						'destination': j ['destination_name'],
						'realtime': j ['realtime'] == '1',
						'location': loc,
						'wait_time': hms2seconds (j ['waittime']),
						'arrival': int (self.last_update + hms2seconds (j ['waittime'])),
					})
				self.data.append (l)
		else:
			self.last_update = 0
	
	def data_age (self):
		'''
		Computes the data's age
		'''
		return (time () - self.last_update)
	
	def lines (self):
		'''
		List lines on the stop
		Return unique indexes as known by the class
		'''
		return (list (range (0, len (self.data))))
	
	def get_line (self, line):
		class Line ():
			'''
			Information about a line on a stop
			'''
			def __init__ (self, data):
				self.id = data ['id']
				self.name = data ['name']
				self.vehicle_type = data ['vehicle_type']
				self.ve = data ['vehicles']
			
			def vehicles (self):
				return (list (range (0, len (self.ve))))
			
			def get_vehicle (self, vehicle):
				class Vehicle ():
					'''
					Information about a vehicle
					'''
					def __init__ (self, data):
						self.id = data ['id']
						self.location = data ['location']
						self.destination = data ['destination']
						self.is_realtime = data ['realtime']
						self.wait_time = data ['wait_time']
						self.arrival = data ['arrival']
				
				return (Vehicle (self.ve [vehicle]))
		
		return (Line (self.data [line]))
	

if __name__ == '__main__':
	from datetime import datetime
	stops = get_stop_list ()
	for i in (3687, 1922, 5832, 3443, 3648):
		print (str (i) + ' (' + stops [i] ['name'] + ') ' + str (stops [i] ['location']))
		s = Stop (i)
		for j in s.lines ():
			l = s.get_line (j)
			print ('\t' + l.vehicle_type + ' ' + l.id + ' (' + l.name + ')')
			for k in l.vehicles ():
				v = l.get_vehicle (k)
				if v.is_realtime:
					print ('\t\t' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)
				else:
					print ('\t\t~' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)