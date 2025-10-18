from abc import ABC, abstractmethod
import math
import pdb
import requests
import re
from datetime import datetime, timedelta

from constants import OBLIQUITY_OF_ECLIPTIC, c, au, day
from naif_id import naif_id

id_map = naif_id()

month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

class hEclPosition(object):
    def __init__(self, time, Lat, Lon, dist, format_code="%Y-%m-%d %H:%M"):
        self.format_code = format_code
        self.time = datetime.strptime(time, format_code)
        self.Lat = Lat
        self.Lon = Lon
        self.dist = dist*au

    def __repr__(self):
        return 'hEclPosition(%s, %s, %s, %s)'%(self.time.strftime(self.format_code), self.Lat, self.Lon, self.dist)


class CelestialObject(ABC):
    """An abstract base class for representing a celestial body."""

    def __init__(self, name):
        """
        Initializes a CelestialObject.

        Args:
            name (str): The name of the celestial object.
        """
        self.name = name

    def __repr__(self):
        return f'CelestialObject(name={self.name})'

    
    def __str__(self):
        """Returns a string representation of the celestial object."""
        return f'{self.name}'


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

    # A list of regexes to capture the mean radius from various formats.
    # Each regex should have one capturing group for the numerical value.
    mean_radius_regexes = [
        r"Vol\. Mean Radius \(km\)\s*=\s*(\d+\.?\d*)\+-",
        r"Vol\. mean radius \(km\)\s*=\s*(\d+\.?\d*)\+-"
    ]

    def __init__(self, name, positions=None, format='json', obj_data=True, make_ephem=True, emphen_type='OBSERVER', center='500@0', start_time=None, stop_time=None, format_code="%Y-%m-%d %H:%M:%S", step_size='1d'):
        """
        Initializes a Planet.

        Args:
            name (str): The name of the planet.
        """
        super().__init__(name)
        self.base_url = 'https://ssd.jpl.nasa.gov/api/horizons.api'
        if format not in ['text', 'json']:
            raise ValueError('format must be either "text" or "json"')
        else:
            self.format = format
        try:
            self._command = id_map[name]
        except KeyError:
            raise ValueError('Object: %s not found in NAIF Id list'%(name))
        if obj_data:
            self.obj_data = 'YES'
        else:
            self.obj_data = 'NO'
        if make_ephem:
            self.make_ephem = 'YES'
        else:
            self.make_ephem = 'NO'
        if emphen_type not in ['OBSERVER', 'VECTORS', 'ELEMENTS', 'SPK', 'APPROACH']:
            raise ValueError('emphen_type must be either "OBSERVER", "VECTORS", "ELEMENTS", "SPK", or "APPROACH"')
        else:
            self.emphen_type = emphen_type
        if center != '500@0':
            raise ValueError('center must be either "500@0"')
        else:
            self.center = center
        
        self.format_code = format_code
        self.query_format_code = '%Y-%m-%d'

        if positions is not None:
            self._positions = positions
        else:
            if start_time is None:
                self._start_time = datetime.today()
            else:
                self._start_time = datetime.strptime(start_time, format_code)

            params = {'format': 'text', 'COMMAND': '%d'%(self._command), 'OBJ_DATA': 'YES', 'MAKE_EPHEM': 'NO'}
            response = requests.get(self.base_url, params=params)
            self._sidereal_period_in_days = self._extract_sidereal_orb_period(response.text)
            self._diameter = 2000 * self._extract_mean_radius(response.text)

            if stop_time is None:
                try:
                    td = timedelta(days=self._sidereal_period_in_days)
                except TypeError:
                    pdb.set_trace()
                self._stop_time = self._start_time + td
            else:
                self._stop_time = datetime.strptime(stop_time, format_code)
            
            self.step_size = step_size
            self._positions = self.orbit()

    def orbit(self):
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
            positions.append(hEclPosition(dt, float(words[3]), float(words[2]), float(words[4])))
        return positions

    def _extract_mean_radius(self, text: str) -> float:
        """
        Extracts the 'Vol. Mean Radius' value measured in kilometers ('km') from
        the provided NASA/JPL Horizons API text and returns it as a float.

        Args:
            text: The input text containing the geophysical properties data.

        Returns:
            The mean radius in kilometers as a float, or None if not found.
        """
        if not self.mean_radius_regexes:
            return None

        for pattern in self.mean_radius_regexes:
            match = re.search(pattern, text)
            if match:
                try:
                    # The number is always in the first capturing group.
                    return float(match.group(1))
                except (ValueError, IndexError):
                    # Continue to the next pattern if conversion fails or groups are not found
                    continue
        return None

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
        return '%s(diameter: %f m == %f s; sidereal period: %f d == %f s)'%(self.name, self.diameter, self.diameter_seconds, self.sidereal_period/day, self.sidereal_period)

    @property
    def diameter(self):
        return self._diameter
    
    @property
    def sidereal_period(self):
        return self._sidereal_period_in_days*day

    @property
    def positions(self):
        return self._positions
    
    @property
    def diameter_seconds(self):
        """Returns the diameter of the object in light-seconds."""
        return self.diameter/c


if __name__ == '__main__':

    planets = {'mercury': Planet(name="Mercury"), 'venus': Planet(name="Venus"), 'earth': Planet(name="Earth"), 'mars': Planet(name="Mars"), 'jupiter': Planet(name="Jupiter"), 'saturn': Planet(name="Saturn"), 'uranus': Planet(name="Uranus"), 'neptune': Planet(name="Neptune")}

    for planet, planet_object in planets.items():
        print(planet_object)

    pdb.set_trace()
    