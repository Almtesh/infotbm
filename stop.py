'''
Fourni les informations sur les arrêts
'''

from libs import get_data_from_json, hms2seconds
from time import time

stop_schedule_url = 'https://ws.infotbm.com/ws/1.0/get-realtime-pass/%d/%s'


class Stop ():
	'''
	Récupère les informations sur un arrêt
	
	data format as returned by infotbm:
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
		d = get_data_from_json (stop_schedule_url % (self.number, self.line)) ['destinations']
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
						'arrival': int (self.last_update + hms2seconds (j ['waittime'])),
					}
					self.data.append (vehicle)
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
				return (list (range (0, len (self.ve))))
			
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
						self.arrival = data ['arrival']
				
				return (Vehicle (self.ve [vehicle]))
		
		return (Line (self.data))
	

if __name__ == '__main__':
	from datetime import datetime
	for i in ((3687, 'A'), (1922, '32')):
		s = Stop (i [0], i [1])
		line = s.get_line ()
		print ('\t' + i [1])
		for k in line.vehicles ():
			v = line.get_vehicle (k)
			if v.is_realtime:
				print ('\t\t' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)
			else:
				print ('\t\t~' + str (v.wait_time) + ' (' + datetime.fromtimestamp (v.arrival).strftime ('%H:%M') + ') → ' + v.destination)