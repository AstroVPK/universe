from datetime import datetime
from constants import c, au


class Location(object):
    def __init__(self, lat, lon, time=None, format_code="%Y-%m-%d %H:%M"):
        self.format_code = format_code
        self.lat = lat
        self.lon = lon
        self.time = time
        if time is not None:
            if isinstance(time, datetime):
                self.time = time
            else:
                self.time = datetime.strptime(time, format_code)

    def __repr__(self):
        if self.time is None:
            return 'Location(%f, %f, %s, %s)'%(self.lat, self.lon, str(self.time), self.format_code)
        else:
            return 'Location(%f, %f, %s, %s)'%(self.lat, self.lon, self.time.strftime(self.format_code), self.format_code)

class hEclPosition(object):
    def __init__(self, hEclLat, hEclLon, dist, time, format_code="%Y-%m-%d %H:%M", distInAU=True):
        self._format_code = format_code
        self._hEclLat = hEclLat
        self._hEclLon = hEclLon
        if distInAU:
            self._dist = dist*au
        else:
            self._dist = dist
        self._dist_seconds = self.dist/c
        self._time = datetime.strptime(time, format_code)

    def __repr__(self):
        return 'hEclPosition(%f, %f, %f, %s, %s)'%(self.hEclLat, self.hEclLon, self.dist, self.time.strftime(self.format_code), self.format_code)
    
    def __str__(self):
        return 'hEclPosition(%f deg hEclLat, %f deg hEclLon, %f AU, %s)'%(self.hEclLat, self.hEclLon, self.dist/au, self.time.strftime(self.format_code))
    
    @property
    def format_code(self):
        return self._format_code

    @property
    def hEclLat(self):
        return self._hEclLat

    @property
    def hEclLon(self):
        return self._hEclLon

    @property
    def dist(self):
        return self._dist

    @property
    def dist_seconds(self):
        return self._dist_seconds

    @property
    def time(self):
        return self._time
