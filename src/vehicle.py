class Vehicle:
    def __init__(
        self, id, destination, realtime, location, wait_time, wait_time_text, arrival
    ):
        self.id = id
        self.destination = destination
        self.realtime = realtime
        self.location = location
        self.wait_time = wait_time
        self.wait_time_text = wait_time_text
        self.arrival = arrival

    def getId(self):
        return self.id

    def getDestination(self):
        return self.destination

    def getRealtime(self):
        return self.realtime

    def getLocation(self):
        return self.location

    def getWaitTime(self):
        return self.wait_time

    def getWaitTimeText(self):
        return self.wait_time_text

    def getArrival(self):
        return self.arrival
