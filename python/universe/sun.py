from coords import Location
from celestial_object_base import CelestialObject


class Sun(CelestialObject):
    _instance = None  # Class-level variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # If no instance exists, create one using the superclass's __new__ method
            cls._instance = super().__new__(cls)
        return cls._instance  # Always return the single instance

    def __init__(self, loc=Location(lat=37.230673, lon=-121.819650), scaled_c=29.0576, format='text', obj_data=True):
        # __init__ will be called every time you try to create an instance,
        # but the instance itself is only created once by __new__.
        # To avoid re-initializing if it's already set, you can add a check.
        if not hasattr(self, '_initialized'):
            super().__init__('SUN', scaled_c=scaled_c, format=format, obj_data=obj_data)
            self._loc = loc
            self._initialized = True

    def __repr__(self):
        return 'Sun(Location(%s, %s))'%(self.loc.lat, self.loc.lon)

    def __str__(self):
        return 'Sun(location=(%s, %s))'%(self.loc.lat, self.loc.lon)

    @property
    def loc(self):
        return self._loc

    @loc.setter
    def loc(self, value):
        self._loc = value


if __name__ == '__main__':
    # Demonstrate the singleton Sun
    instance1 = Sun()
    print(f"Instance 1 location: {instance1.loc}")

    instance2 = Sun(Location(lat=37.219403, lon=-121.851214)) # This will return the same instance as instance1
    print(f"Instance 2 location: {instance2.loc}")

    print(f"Are instance1 and instance2 the same object? {instance1 is instance2}")
    print(f"Value of instance1 after instance2 creation: {instance1.loc}")