from datetime import datetime
from constants import au


class hEclPosition(object):
    def __init__(self, time, Lat, Lon, dist, format_code="%Y-%m-%d %H:%M"):
        self.format_code = format_code
        self.time = datetime.strptime(time, format_code)
        self.Lat = Lat
        self.Lon = Lon
        self.dist = dist*au

    def __repr__(self):
        return 'hEclPosition(%s, %s, %s, %s)'%(self.time.strftime(self.format_code), self.Lat, self.Lon, self.dist)