from abc import ABC, abstractmethod
import math
import pdb

from query import JPLQuery
from constants import OBLIQUITY_OF_ECLIPTIC, c, au
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
        r"Sidereal orb\. per\.\s*=\s*(\d+\.?\d*)\s*([a-zA-Z]?)",
        r"Sidereal orb\. per\.,\s*(?:[a-zA-Z])\s*=\s*(\d+\.?\d*)",
        r"Sidereal orb period\s*=\s*(\d+\.?\d*)\s*([a-zA-Z]?)",
        r"Mean sidereal orb per\s*=\s*(\d+\.?\d*)\s*([a-zA-Z]?)",
        r"Sidereal orbit period\s*=\s*(\d+\.?\d*)\s*([a-zA-Z]?)"
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
            self.diameter = query.diameter

    def __repr__(self):
        return 'Planet(name=%s, diameter=%d)'%(self.name, self.diameter)

    def __str__(self):
        """Returns a string representation of the Planet."""
        return '%s(diameter: %d m == %d s)'%(self.name, self.diameter, self.diameter_in_seconds)

    @property
    def positions(self):
        return self._positions
    
    @property
    def diameter_in_seconds(self):
        """Returns the diameter of the object in light-seconds."""
        return self.diameter / c

    @diameter_in_seconds.setter
    def diameter_in_seconds(self, seconds):
        """Sets the diameter from a value in light-seconds."""
        self.diameter = seconds * c


if __name__ == '__main__':

    mercury = Planet(name="Mercury")
    venus = Planet(name="Venus")
    earth = Planet(name="Earth")
    mars = Planet(name="Mars")
    jupiter = Planet(name="Jupiter")
    saturn = Planet(name="Saturn")
    uranus = Planet(name="Uranus")
    neptune = Planet(name="Neptune")

    pdb.set_trace()
    