from utils import get_data_from_json, hms2seconds
from time import time
from vehicle import Vehicle


SCHEDULE_URL = "https://ws.infotbm.com/ws/1.0/get-realtime-pass/%d/%s"


class Line:
    """
    Information on the line served at a stop.
    """

    def __init__(self, vehicles):
        self.vehicles = vehicles

    def get_vehicles(self):
        if self.vehicles is not None:
            return list(range(0, len(self.vehicles)))
        return []

    def get_vehicle(self, vehicle_id):
        return self.vehicles[vehicle_id]


class StopRoute:
    def __init__(
        self,
        number,
        line,
        auto_update_at_creation=True,
        auto_update=False,
        auto_update_delay=-1,
    ):
        self.number = number
        self.line = line
        self.last_update = 0
        self.data = None
        if auto_update_at_creation:
            self.update()

    def update(self, auto=False):
        """
        Update data.
        """

        data = get_data_from_json(SCHEDULE_URL % (self.number, self.line))
        if "destinations" in data:
            data = data["destinations"]
        else:
            print("No data for stop %d" % self.number)
            return
        self.last_update = time()
        if type(data) == dict:
            self.data = []
            # let's simplify the data
            for i in data:
                for j in data[i]:
                    location = None
                    try:
                        location = (
                            float(j["vehicle_lattitude"]),
                            float(j["vehicle_longitude"]),
                        )
                    except TypeError:
                        pass
                    vehicle = Vehicle(
                        j["vehicle_id"],
                        j["destination_name"],
                        j["realtime"] == "1",
                        location,
                        hms2seconds(j["waittime"]),
                        j["waittime_text"],
                        int(self.last_update + hms2seconds(j["waittime"])),
                    )
                    self.data.append(vehicle)
            self.data = sorted(self.data, key=lambda vehicle: vehicle.getArrival())
        else:
            self.last_update = 0

    def data_age(self):
        """
        Returns the age of the data.
        """

        return time() - self.last_update

    def get_line(self):
        return Line(self.data)
