import re
import requests
from abc import ABC
import pdb

from naif_id import naif_id
from constants import OBLIQUITY_OF_ECLIPTIC, c, day


id_map = naif_id()


class CelestialObject(ABC):
    """An abstract base class for representing a celestial body."""
    base_url = 'https://ssd.jpl.nasa.gov/api/horizons.api'

    # A list of regexes to capture the mean radius from various formats.
    # Each regex should have one capturing group for the numerical value.
    mean_radius_regexes = [
        r"Vol\. Mean Radius \(km\)\s*=\s*(\d+\.?\d*)\+-",
        r"Vol\. mean radius \(km\)\s*=\s*(\d+\.?\d*)\+-",
        r"Radius \(photosphere\)\s*=\s*(\d+\.?\d*)\s*km"
    ]

    def __init__(self, name, scaled_c=29.0576, format='text', obj_data=True):
        """
        Initializes a CelestialObject.

        Args:
            name (str): The name of the celestial object.
        """
        self.name = name
        self._scaled_c = scaled_c
        if format not in ['text', 'json']:
            raise ValueError('format must be either "text" or "json"')
        else:
            self.format = format
        if obj_data:
            self.obj_data = 'YES'
        else:
            self.obj_data = 'NO'
        try:
            self._command = id_map[name]
        except KeyError:
            raise ValueError('Object: %s not found in NAIF Id list'%(name))

        params = {'format': self.format, 'COMMAND': '%d'%(self._command), 'OBJ_DATA': 'YES', 'MAKE_EPHEM': 'NO'}
        self.response = requests.get(self.base_url, params=params)
        self._diam = 2000*self._extract_mean_radius(self.response.text)

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

    @property
    def scaled_c(self):
        return self._scaled_c

    @property
    def diam_seconds(self):
        """Returns the diameter of the object in light-seconds."""
        return self.diam/c

    @property
    def diam(self):
        return self._diam

    @property
    def scaled_diam(self):
        return self.diam_seconds*self.scaled_c

    def __repr__(self):
        return f'CelestialObject(name={self.name})'

    def __str__(self):
        """Returns a string representation of the celestial object."""
        return f'{self.name}'
    
    @scaled_c.setter
    def scaled_c(self, value):
        self._scaled_c = value