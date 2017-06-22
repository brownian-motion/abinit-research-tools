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

    """Interprets the given dict `parsed_object` as a `KPointWithEnergy`"""
    def object_hook(self, parsed_object):
        # Remember - reading unicode strings from json!
        if((u'_type' in parsed_object and parsed_object[u'_type'] == u'Coordinate') or u'coordinate_array' in parsed_object):
            return Coordinate(parsed_object[u'coordinate_array'],parsed_object[u'coordinate_system'])
        elif((u'_type' in parsed_object and parsed_object[u'_type'] == u'KPointWithEnergy') or u'nband' in parsed_object):
            return KPointWithEnergy(parsed_object[u'number'], parsed_object[u'nband'], parsed_object[u'wtk'], parsed_object[u'coord'], parsed_object[u'band_energies'], parsed_object[u'energy_unit'])
        # if(('_type' in parsed_object and parsed_object._type == 'Coordinate') or 'coordinate_array' in parsed_object):
        #     return Coordinate(parsed_object['coordinate_array'],parsed_object['coordinate_system'])
        # elif(('_type' in parsed_object and parsed_object._type == 'KPointWithEnergy') or 'nband' in parsed_object):
        #     return KPointWithEnergy(parsed_object['number'], parsed_object['nband'], parsed_object['wtk'], parsed_object['coord'], parsed_object['band_energies'], parsed_object['energy_unit'])
        else:
            # print("couldn't parse correctly: ")
            print(parsed_object)
            return parsed_object    

class CoordinateJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    """Interprets the given dict `object` as a `KPointWithEnergy`"""
    def object_hook(self, object):
        return Coordinate(object.coordinate_array, object.coordinate_system)
