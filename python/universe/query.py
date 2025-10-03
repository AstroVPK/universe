import requests
from datetime import datetime
import pdb

from naif_id import naif_id

id = naif_id()

class JPLQuery(object):
    def __init__(self, object, format='json', obj_data=True, make_ephem=True, emphen_type='OBSERVER', center='500@0', start_time=datetime.today(), stop_time=None):
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
        self._start_time = start_time
        if stop_time is None:
            params = {'format': 'json', 'COMMAND': '%d'%(self.command), 'OBJ_DATA': 'YES', 'MAKE_EPHEM': 'NO'}
            pdb.set_trace()
            response = requests.get(self.base_url, params=params)
            print(response.json()) # Assuming the response is in JSON format
            pdb.set_trace()
        else:
            self._stop_time = stop_time

        

    

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


if __name__ == '__main__':
    query = JPLQuery('earth')
    print(query.command)