import json
from json import JSONEncoder, JSONDecoder

class KPointWithEnergy:
    """Simple data type for a k-point with energy eigenvalues for various bands"""
    def __init__(self, number, num_bands, wtk, coord, band_energies, energy_unit="unknown"):
        self.number = number
        self.nband = num_bands
        self.wtk = wtk
        self.coord = coord
        self.band_energies = band_energies
        self.energy_unit = energy_unit

    def __repr__(self):
        return json.dumps(self.__dict__, cls=SimpleObjectJSONEncoder)

class Coordinate:
    """
    Simple data type for a coordinate.
    Every Coordinate is an array of numbers representing the coordinate position,
    and a string describing the coordinate system.
    """
    def __init__(self, coordinate_array, coordinate_system="unknown"):
        self.coordinate_array = coordinate_array
        self.coordinate_system = coordinate_system

    def __repr__(self):
        return json.dumps(self.__dict__, cls=SimpleObjectJSONEncoder)

class SimpleObjectJSONEncoder(JSONEncoder):
    """Encodes objects into JSON using their __dict__ form"""
    def default(self, o):
        """Encodes the object o using o.__dict___"""
        return o.__dict__

class KPointWithEnergyJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    """Interprets the given dict `object` as a `KPointWithEnergy`"""
    def object_hook(self, object):
        return KPointWithEnergy(object.number, object.num_bands, object.wtk, json.load(object.coord, cls=CoordinateJSONDecoder ), object.band_energies, object.energy_unit)

class CoordinateJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    """Interprets the given dict `object` as a `KPointWithEnergy`"""
    def object_hook(self, object):
        return Coordinate(object.coordinate_array, object.coordinate_system)
