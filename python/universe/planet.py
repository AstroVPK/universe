import math
import pdb
import requests
import re
from datetime import datetime, timedelta

from constants import OBLIQUITY_OF_ECLIPTIC, c, day
from naif_id import naif_id
from coords import hEclPosition, Location
from celestial_object_base import CelestialObject
from sun import Sun


id_map = naif_id()

month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}


class Planet(CelestialObject):
    """Represents a planet, inheriting from CelestialObject."""

    # A list of regexes to capture the orbital period and unit from various formats.
    # Each regex should have two capturing groups:
    # 1. The numerical value (float or int).
    # 2. The unit (optional character).
    orbital_period_regexes = [
        r"Sidereal orb\. per\.\s*=\s*(\d+\.?\d*)\s*(d)",
        r"Sidereal orb\. per\.,\s*(?:d)\s*=\s*(\d+\.?\d*)",
        r"Sidereal orb period\s*=\s*(\d+\.?\d*)\s*(d)",
        r"Mean sidereal orb per\s*=\s*(\d+\.?\d*)\s*(d)",
        r"Sidereal orbit period\s*=\s*(\d+\.?\d*)\s*(d)"
    ]

    def __init__(self, name, scaled_c=29.0576, format='text', obj_data=True, make_ephem=True, ephem_type='OBSERVER', center='500@0', sun=Sun(), start_time=None, stop_time=None, format_code="%Y-%m-%d %H:%M:%S", step_size='1d'):
        """
        Initializes a Planet.

        Args:
            name (str): The name of the planet.
        """
        super().__init__(name, scaled_c=scaled_c, format=format, obj_data=obj_data)
        if make_ephem:
            self.make_ephem = 'YES'
        else:
            self.make_ephem = 'NO'
        if ephem_type not in ['OBSERVER', 'VECTORS', 'ELEMENTS', 'SPK', 'APPROACH']:
            raise ValueError('emphen_type must be either "OBSERVER", "VECTORS", "ELEMENTS", "SPK", or "APPROACH"')
        else:
            self.ephem_type = ephem_type
        if center != '500@0':
            raise ValueError('center must be "500@0"')
        else:
            self.center = center
        self._sun = sun
        
        self.format_code = format_code
        self.query_format_code = '%Y-%m-%d'

        if start_time is None:
            self._start_time = datetime.today()
        else:
            self._start_time = datetime.strptime(start_time, format_code)

        self._sidereal_period_in_days = self._extract_sidereal_orb_period(self.response.text)
        self._diam = 2000*self._extract_mean_radius(self.response.text)

        if stop_time is None:
            try:
                td = timedelta(days=self._sidereal_period_in_days)
            except TypeError:
                pdb.set_trace()
            self._stop_time = self._start_time + td
        else:
            self._stop_time = datetime.strptime(stop_time, format_code)
        
        self.step_size = step_size
        self._orbit = self._get_orbit()
        self._position = self._get_positions()
    
    def _get_orbit(self):
        params = {'format': 'text', 'COMMAND': '%d'%(self._command), 'OBJ_DATA': 'NO', 'MAKE_EPHEM': 'YES', 'EPHEM_TYPE': 'OBSERVER', 'CENTER': self.center, 'START_TIME': self._start_time.strftime(self.query_format_code), 'STOP_TIME': self._stop_time.strftime(self.query_format_code), 'STEP_SIZE': self.step_size, 'QUANTITIES': "'18,20'" }
        response = requests.get(self.base_url, params=params)
        lines = response.text.split('\n')
        start = None
        stop = None
        for lineno, line in enumerate(lines):
            if line == '$$SOE':
                start = lineno + 1
                continue
            if line == '$$EOE':
                stop = lineno - 1
                break
        positions = list()
        for line in lines[start:stop+1]:
            words = line.split()
            text_date = words[0].split('-')
            text_time = words[1].split(':')
            dt = '%s-%s-%s %s:%s'%(text_date[0], str(month[text_date[1]]), text_date[2], text_time[0], text_time[1])
            positions.append(hEclPosition(float(words[3]), float(words[2]), float(words[4]), dt))
        return positions

    def _get_positions(self):
        R = 6356752 # Polar radius of the Earth in m. Polar because the polar radius is slightly smaller than the equatorial radius
        slat = math.radians(self.sun.loc.lat)
        slon = math.radians(self.sun.loc.lon)
        positions = list()
        for pos in self._orbit:
            dByR = (pos.dist_seconds*self.scaled_c)/R
            brng = math.radians(pos.hEclLon)
            lat = math.asin(math.sin(slat)*math.cos(dByR) + math.cos(slat)*math.sin(dByR)*math.cos(brng))
            lon = slon + math.atan2(math.sin(brng)*math.sin(dByR)*math.cos(slat),(math.cos(dByR)-math.sin(slat)*math.sin(lat)))
            loc = Location(math.degrees(lat), math.degrees(lon), time=pos.time, format_code=pos.format_code)
            positions.append(loc)
        return positions

    def _extract_sidereal_orb_period(self, text: str) -> float | None:
        """
        Extracts the 'Sidereal orb period' value measured in days ('d') from 
        the provided NASA/JPL Horizons API text and returns it as a float.

        Args:
            text: The input text containing the geophysical properties data.

        Returns:
            The sidereal orb period in days as a float, or None if not found.
        """
        if not self.orbital_period_regexes:
            return None
        
        for pattern in self.orbital_period_regexes:
            match = re.search(pattern, text)
            if match:
                try:
                    # The number is always in the first capturing group.
                    return float(match.group(1))
                except (ValueError, IndexError):
                    # Continue to the next pattern if conversion fails or groups are not found
                    continue
        return None

    def __repr__(self):
        return 'Planet(name=%s)'%(self.name)

    def __str__(self):
        """Returns a string representation of the Planet."""
        return '%s(%s; diameter: %f m == %f s; sidereal period: %f d == %f s)'%(self.name, self.sun, self.diam, self.diam_seconds, self.sidereal_period/day, self.sidereal_period)

    @property
    def sidereal_period(self):
        return self._sidereal_period_in_days*day

    @property
    def orbit(self):
        return self._orbit
    
    @property
    def position(self):
        return self._position

    @property
    def sun(self):
        return self._sun

    @CelestialObject.scaled_c.setter
    def scaled_c(self, value):
        self._scaled_c = value
        self._position = self._get_positions()


if __name__ == '__main__':

    planets = {'mercury': Planet(name="Mercury"), 'venus': Planet(name="Venus"), 'earth': Planet(name="Earth"), 'mars': Planet(name="Mars"), 'jupiter': Planet(name="Jupiter"), 'saturn': Planet(name="Saturn"), 'uranus': Planet(name="Uranus"), 'neptune': Planet(name="Neptune")}

    for planet, planet_object in planets.items():
        print(planet_object)

    pdb.set_trace()
    