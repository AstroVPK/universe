from abc import ABC, abstractmethod
import math
import pdb

from query import JPLQuery
from constants import OBLIQUITY_OF_ECLIPTIC, c, au, day
from naif_id import naif_id


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

    def __init__(self, name, positions=None):
        """
        Initializes a Planet.

        Args:
            name (str): The name of the planet.

        """
        super().__init__(name)
        if positions is not None:
            self._positions = positions
        else:
            query = JPLQuery(self.name, orbital_period_regexes=self.orbital_period_regexes, mean_radius_regexes=self.mean_radius_regexes)
            self._positions = query.orbit()
            self._diameter = query.diameter
            self._sidereal_period = query.sidereal_period

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
        return self._sidereal_period

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
    