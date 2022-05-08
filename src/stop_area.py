from utils import get_data_from_json
from urllib.parse import quote


STOP_URL = "https://ws.infotbm.com/ws/1.0/get-schedule/%s"


class StopArea:
    def __init__(self, id, name, city):
        self.id = id
        self.name = name
        self.city = city

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getCity(self):
        return self.city

    def __repr__(self):
        return self.name + " (" + self.city + ")" + " (id: " + self.id + ")"

    def __str__(self):
        return self.name + " (" + self.city + ")" + " (id: " + self.id + ")"


# we on only treat stops of type "stop_area"
def get_stop_areas_by_name(keyword):
    data = get_data_from_json(STOP_URL % quote(keyword))
    stopAreas = []
    for s in data:
        if s["type"] == "stop_area":
            stopAreas.append(StopArea(s["id"], s["name"], s["city"]))
    return stopAreas