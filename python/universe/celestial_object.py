from abc import ABC, abstractmethod
import math
import pdb

from query import JPLQuery
from constants import OBLIQUITY_OF_ECLIPTIC, c, au
from naif_id import naif_id


class CelestialObject(ABC):
    """An abstract base class for representing a celestial body."""

    def __init__(self, name, diameter):
        """
        Initializes a CelestialObject.

        Args:
            name (str): The name of the celestial object.
            diameter (float): The diameter of the object in meters.
            parent (CelestialObject, optional): The parent body. Defaults to None.
        """
        self.name = name
        self.diameter = diameter


    def __repr__(self):
        return 'CelestialObject(name=%s, diameter=%d)'%(self.name, self.diameter)

    
    def __str__(self):
        """Returns a string representation of the celestial object."""
        return '%s(diameter: %d m == %d s)'%(self.name, self.diameter, self.diameter_in_seconds)



    @property
    def diameter_in_seconds(self):
        """Returns the diameter of the object in light-seconds."""
        return self.diameter / c

    @diameter_in_seconds.setter
    def diameter_in_seconds(self, seconds):
        """Sets the diameter from a value in light-seconds."""
        self.diameter = seconds * c


class Planet(CelestialObject):
    """Represents a planet, inheriting from CelestialObject."""

    def __init__(self, name, diameter, positions=None):
        """
        Initializes a Planet.

        Args:
            name (str): The name of the planet.
            diameter (float): The diameter of the planet in meters.

        """
        super().__init__(name, diameter)
        if positions is not None:
            self._positions = positions
        else:
            query = JPLQuery(self.name)
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


if __name__ == '__main__':
    # Example of how to use the CelestialObject.
    # This class is intended to be subclassed, not instantiated directly.

    mercury = Planet(name="Mercury", diameter=6779000)
    venus = Planet(name="Venus", diameter=6779000)    
    earth = Planet(name="Earth", diameter=12742000)
    mars = Planet(name="Mars", diameter=6779000)
    jupiter = Planet(name="Jupiter", diameter=12742000)
    saturn = Planet(name="Saturn", diameter=6779000)
    uranus = Planet(name="Uranus", diameter=12742000)
    neptune = Planet(name="Neptune", diameter=6779000)

    pdb.set_trace()
    