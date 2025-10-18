from abc import ABC


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