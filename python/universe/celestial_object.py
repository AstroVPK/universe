from abc import ABC, abstractmethod
import math

from .constants import OBLIQUITY_OF_ECLIPTIC, c

class CelestialObject(ABC):
    """An abstract base class for representing a celestial body."""

    def __init__(self, name, ra, dec, diameter, distance, parent=None):
        """
        Initializes a CelestialObject.

        Args:
            name (str): The name of the celestial object.
            ra (float): The Right Ascension of the object in hours.
            dec (float): The Declination of the object in degrees.
            diameter (float): The diameter of the object in meters.
            distance (float): The distance to the object in meters.
            parent (CelestialObject, optional): The parent body. Defaults to None.
        """
        self.name = name
        self.RA = ra
        self.Dec = dec
        self.diameter = diameter
        self.distance = distance
        self.parent = parent

    def __str__(self):
        """Returns a string representation of the celestial object."""
        return (f"{self.name} (RA: {self.RA:.2f}h, Dec: {self.Dec:.2f}°, "
                f"Diameter: {self.diameter / 1000:.2e} km, Distance: {self.distance / 1000:.2e} km)")

    def ecliptic_coordinates(self):
        """
        Calculates the ecliptic coordinates (longitude and latitude) from
        the object's equatorial coordinates (RA and Dec).

        Returns:
            tuple: A tuple containing the ecliptic longitude and latitude
                   in degrees.
        """
        # Convert RA from hours to degrees, then to radians
        ra_rad = math.radians(self.RA * 15)
        # Convert Dec to radians
        dec_rad = math.radians(self.Dec)
        # Convert obliquity to radians
        e_rad = math.radians(OBLIQUITY_OF_ECLIPTIC)

        # Ecliptic latitude (β)
        sin_beta = (math.sin(dec_rad) * math.cos(e_rad) -
                    math.cos(dec_rad) * math.sin(e_rad) * math.sin(ra_rad))
        beta = math.degrees(math.asin(sin_beta))

        # Ecliptic longitude (λ)
        y = math.sin(ra_rad) * math.cos(e_rad) + math.tan(dec_rad) * math.sin(e_rad)
        x = math.cos(ra_rad)
        lambda_ = math.degrees(math.atan2(y, x))

        return (lambda_ + 360) % 360, beta

    @property
    def diameter_in_seconds(self):
        """Returns the diameter of the object in light-seconds."""
        return self.diameter / c

    @diameter_in_seconds.setter
    def diameter_in_seconds(self, seconds):
        """Sets the diameter from a value in light-seconds."""
        self.diameter = seconds * c

    @property
    def distance_in_seconds(self):
        """Returns the distance to the object in light-seconds."""
        return self.distance / c

    @distance_in_seconds.setter
    def distance_in_seconds(self, seconds):
        """Sets the distance from a value in light-seconds."""
        self.distance = seconds * c

    @abstractmethod
    def draw(self):
        """
        A placeholder method for drawing the object.
        Subclasses should implement this method to provide specific
        drawing logic, for example, creating a KML representation.
        """
        pass


if __name__ == '__main__':
    # Example of how to use the CelestialObject.
    # This class is intended to be subclassed, not instantiated directly.
    class Star(CelestialObject):
        def draw(self):
            print(f"Drawing a star: {self.name}")
    
    sirius = Star(name="Sirius", ra=6.75, dec=-16.72, diameter=2.4e9, distance=8.13e16)
    print(sirius)
    sirius.draw()
    ecliptic_lon, ecliptic_lat = sirius.ecliptic_coordinates()
    print(f"Ecliptic Coords for {sirius.name}: Longitude={ecliptic_lon:.2f}°, Latitude={ecliptic_lat:.2f}°")
    print(f"Diameter of {sirius.name} in light-seconds: {sirius.diameter_in_seconds:.4f}s")
    print(f"Distance to {sirius.name} in light-seconds: {sirius.distance_in_seconds:.2f}s")

    # Demonstrate using the setter
    print("\n--- Demonstrating property setter ---")
    sirius.distance_in_seconds = 271.19  # This is 8.58 light-years
    print(f"Updated distance for {sirius.name} to {sirius.distance_in_seconds:.2f} light-seconds.")
    print(sirius)