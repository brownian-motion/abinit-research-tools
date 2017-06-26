import json
from json import JSONEncoder, JSONDecoder
from fractions import Fraction

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


MIN_LABEL_WIDTH = 8
class SimpleAttribute:

    def __init__(self, name, value, comment=None):
        self.name = name
        self.value = value
        self.comment = comment

    def __str__(self):
        """Represent this attribute in Abinit"""
        if(self.comment is None):
            formatted_comment_lines = []
        else:
            formatted_comment_lines = ["#"+x for x in self.comment.splitlines()]

        if(self.value is None or self.name is None):
            input_lines=[]
        else:
            if(type(self.value) is list and len(self.value) > 0):
                if(type(self.value[0]) is list): #then the value is a matrix
                    input_lines = [self.name] + [' '*MIN_LABEL_WIDTH+"  ".join([unicode(xy) for xy in x]) for x in self.value]
                else: #then the value is a 1-D array
                    input_lines = [self.name.ljust(MIN_LABEL_WIDTH) + " " + "  ".join([unicode(x) for x in self.value])]
            else:
                input_lines = [self.name.ljust(MIN_LABEL_WIDTH) + " "+ unicode(self.value)]

        return "\n".join(formatted_comment_lines+input_lines)

    def __repr__(self):
        """Represent this attribute as JSON"""
        return self.__dict__.__repr__()

class SimpleAttributeJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, element):
        """
        Parse the name, value, and optional comment inside an attribute,
        and return it as a SimpleAttribute.

        Assumes all element properties are unicode u'strings'.
        """
        try:
            if u'_type' in element and element[u'_type'] == u'fraction':
                if 'numerator' in element and 'denominator' in element:
                    return Fraction(int(element['numerator']), int(element['denominator']))
                elif 'value' in element:
                    return Fraction(element['value'])
                raise NotImplementedError("Unknown Fraction format: "+element)
            # handle_command_line_IO.errprint(element)
            if ('_type' in element and element['_type'] == u'attribute') \
                or 'comment' in element \
                or 'name' in element \
                or 'value' in element: #if it's a Simple Attribute

                if u'comment' in element: 
                    if u'name' in element and u'value' in element:
                        return SimpleAttribute(name=(element[u'name'] or element['name']), value=element[u'value'], comment=element[u'comment'])
                    return SimpleAttribute(name=None, value=None, comment=element[u'comment'])
                return SimpleAttribute(name=element[u'name'], value=element[u'value'])
            return element
        except Exception as cause:
            if not cause.args: 
                cause.args=('',)
            cause.args = cause.args + ("Encountered error with: "+str(element),)
            raise
