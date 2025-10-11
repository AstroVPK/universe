import requests
import re
from datetime import datetime, timedelta
import pdb

from naif_id import naif_id
import constants

id = naif_id()


month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

class hEclPosition(object):
    def __init__(self, time, Lat, Lon, dist, format_code="%Y-%m-%d %H:%M"):
        self.format_code = format_code
        self.time = datetime.strptime(time, format_code)
        self.Lat = Lat
        self.Lon = Lon
        self.dist = dist*constants.au

    def __repr__(self):
        return 'hEclPosition(%s, %s, %s, %s)'%(self.time.strftime(self.format_code), self.Lat, self.Lon, self.dist)



class JPLQuery(object):
    def __init__(self, object, format='json', obj_data=True, make_ephem=True, emphen_type='OBSERVER', center='500@0', start_time=None, stop_time=None, format_code="%Y-%m-%d %H:%M:%S", step_size='1d'):
        self.base_url = 'https://ssd.jpl.nasa.gov/api/horizons.api'
        if format not in ['text', 'json']:
            raise ValueError('format must be either "text" or "json"')
        else:
            self.format = format
        try:
            self._object = object
            self._command = id[object]
        except KeyError:
            raise ValueError('Object: %s not found in NAIF Id list'%(object))
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
        if start_time is None:
            self._start_time = datetime.today()
        else:
            self._start_time = datetime.strptime(start_time, format_code)
        if stop_time is None:
            params = {'format': 'text', 'COMMAND': '%d'%(self.command), 'OBJ_DATA': 'YES', 'MAKE_EPHEM': 'NO'}
            response = requests.get(self.base_url, params=params)
            self._sidereal_period_in_days = self._extract_sidereal_orb_period(response.text)
            try:
                td = timedelta(days=self._sidereal_period_in_days)
            except TypeError:
                pdb.set_trace()
            self._stop_time = self._start_time + timedelta(days=self._sidereal_period_in_days)
        else:
            self._stop_time = datetime.strptime(stop_time, format_code)
        self.step_size = step_size
        self._diameter = 2000*self._extract_mean_radius(response.text)

    def orbit(self):
        params = {'format': 'text', 'COMMAND': '%d'%(self.command), 'OBJ_DATA': 'NO', 'MAKE_EPHEM': 'YES', 'EPHEM_TYPE': 'OBSERVER', 'CENTER': self.center, 'START_TIME': self._start_time.strftime(self.query_format_code), 'STOP_TIME': self._stop_time.strftime(self.query_format_code), 'STEP_SIZE': self.step_size, 'QUANTITIES': "'18,20'" }
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
        Extracts the 'Vol. Mean Radus' value measured in kilometers ('km') from 
        the provided NASA/JPL Horizons API text and returns it as a float.

        Args:
            text: The input text containing the geophysical properties data.

        Returns:
            The mean radius in kilometers as a float, or None if not found.
        """
        # Pattern looks for: 'Vol. Mean Radius (km) = ' followed by a number (captured in group 1) 
        # and then the unit ' km' (with optional spaces).
        pattern = r"=\s*(\d+\.?\d*)"

        # re.search is used to find the single matching period in days.
        match = re.search(pattern, text)

        if match:
            # Group 1 is the captured numerical string (e.g., "365.25636")
            try:
                return float(match.group(1))
            except ValueError:
                # This handles unexpected non-numeric content if the regex somehow matched
                print(f"Error converting extracted value to float: {match.group(1)}")
                return None
        
        return None

    def _extract_sidereal_orb_period(self, text: str) -> float:
        """
        Extracts the 'Sidereal orb period' value measured in days ('d') from 
        the provided NASA/JPL Horizons API text and returns it as a float.

        Args:
            text: The input text containing the geophysical properties data.

        Returns:
            The sidereal orb period in days as a float, or None if not found.
        """
        # Pattern looks for: 'Sidereal orb period = ' followed by a number (captured in group 1) 
        # and then the unit ' d' (with optional spaces).
        pattern = r"(?:Sidereal orb period|Mean sidereal orb per|Sidereal orb\.\s*per\.)(?:\s*,\s*d)?\s*=\s*(\d+\.?\d*)\s*d?"

        # re.search is used to find the single matching period in days.
        match = re.search(pattern, text)

        if match:
            # Group 1 is the captured numerical string (e.g., "365.25636")
            try:
                return float(match.group(1))
            except ValueError:
                # This handles unexpected non-numeric content if the regex somehow matched
                print(f"Error converting extracted value to float: {match.group(1)}")
                return None
        
        return None

    @property
    def object(self):
        return self._object
    
    @object.setter
    def object(self, object):
        self._object = object
        self._command = id[object]

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        self._command = command
        self._object = list(id.keys())[list(id.values()).index(command)]

    @property
    def sidereal_period_in_days(self):
        return self._sidereal_period_in_days

    @property
    def start_time(self):
        return self._start_time.strftime(self.format_code)

    @start_time.setter
    def start_time(self, value):
        self._start_time = datetime.strptime(value, format_code)
        self._stop_time = self._start_time + timedelta(days=self._sidereal_period_in_days)

    @property
    def stop_time(self):
        return self._stop_time.strftime(self.format_code)

    @property
    def diameter(self):
        return self._diameter

if __name__ == '__main__':
    query = JPLQuery('earth')
    query.orbit()
    print(query)