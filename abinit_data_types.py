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

    Implements scalar addition, subtraction, multiplication, and division.
    """
    def __init__(self, coordinate_array, coordinate_system="unknown"):
        self.coordinate_array = Coordinate.parse_coordinate_value_array(coordinate_array)
        self.coordinate_system = coordinate_system

    def __repr__(self):
        """Represents this Coordinate as a JSON object"""
        return json.dumps(self.__dict__, cls=SimpleObjectJSONEncoder)

    def __eq__(self, other):
        """Returns whether this Coordinate and the other coordinate have the same data"""
        if self.coordinate_system != other.coordinate_system \
            or len(self.coordinate_array) != len(other.coordinate_array):
            return False
        for i in xrange(0, len(self.coordinate_array)):
            if self.coordinate_array[i] != other.coordinate_array[i]:
                return False
        return True

    def __add__(self, other):
        """
        If other is scalar, returns a new Coordinate with each coordinate increased by value other.
        If other is a list, returns a new Coordinate with each coordinate increased
            by the value of other at that index.
            If there lists are not the same length, raises a RuntimeException
        """
        if isinstance(other, Coordinate):
            if self.coordinate_system != other.coordinate_system:
                raise RuntimeError('incompatible coordinate systems: '\
                    +self.coordinate_system+' and '+other.coordinate_system)
            return self+other.coordinate_array
        elif isinstance(other, list):
            return Coordinate(\
                coordinate_array=\
                    [self.coordinate_array[i]+other[i] for i in xrange(len(self.coordinate_array))],
                coordinate_system=self.coordinate_system)
        else:
            return Coordinate([x+other for x in self.coordinate_array], self.coordinate_system)

    def __sub__(self, other):
        """
        If other is scalar, returns a new Coordinate with each coordinate decreased by value other.
        If other is a list, returns a new Coordinate with each coordinate decreased
            by the value of other at that index.
            If there lists are not the same length, raises a RuntimeException
        """
        if isinstance(other, Coordinate):
            if self.coordinate_system != other.coordinate_system:
                raise RuntimeError('incompatible coordinate systems: '\
                    +self.coordinate_system+' and '+other.coordinate_system)
            return self-other.coordinate_array
        elif isinstance(other, list):
            return Coordinate(\
                coordinate_array=\
                    [self.coordinate_array[i]-other[i] for i in xrange(len(self.coordinate_array))],
                coordinate_system=self.coordinate_system)
        else:
            return Coordinate([x-other for x in self.coordinate_array], self.coordinate_system)

    def __mul__(self, other):
        """
        If other is scalar, returns a new Coordinate with each coordinate multiplied by value other.
        If other is a list, returns a new Coordinate with each coordinate multiplied
            by the value of other at that index.
            If there lists are not the same length, raises a RuntimeException
        """
        if isinstance(other, Coordinate):
            if self.coordinate_system != other.coordinate_system:
                raise RuntimeError('incompatible coordinate systems: '\
                    +self.coordinate_system+' and '+other.coordinate_system)
            return self*other.coordinate_array
        elif isinstance(other, list):
            return Coordinate(\
                coordinate_array=\
                    [self.coordinate_array[i]*other[i] for i in xrange(len(self.coordinate_array))],
                coordinate_system=self.coordinate_system)
        else:
            return Coordinate([x*other for x in self.coordinate_array], self.coordinate_system)

    def __div__(self, other):
        """
        If other is scalar, returns a new Coordinate with each coordinate divided by value other.
        If other is a list, returns a new Coordinate with each coordinate divided
            by the value of other at that index.
            If there lists are not the same length, raises a RuntimeException
        """
        if isinstance(other, Coordinate):
            if self.coordinate_system != other.coordinate_system:
                raise RuntimeError('incompatible coordinate systems: '\
                    +self.coordinate_system+' and '+other.coordinate_system)
            return self/other.coordinate_array
        elif isinstance(other, list):
            return Coordinate(\
                coordinate_array=\
                    [self.coordinate_array[i]/other[i] for i in xrange(len(self.coordinate_array))],
                coordinate_system=self.coordinate_system)
        else:
            return Coordinate([x/other for x in self.coordinate_array], self.coordinate_system)

    def __hash__(self):
        """
        Performs a unique has on this object determined
        from the coordinate system and the coordinate values
        """
        return hash((self.coordinate_system, tuple(self.coordinate_array)))

    def norm(self):
        """
        Returns the length of this vector
        """
        return sum([val * val for val in self.coordinate_array])**0.5

    @staticmethod
    def parse_coordinate_value_array(raw_coordinate_array):
        """
        Parses numerical data from a raw_coordinate_array,
        and returns a new array representing that data in native python types.

        Currently-supported types are int, float, and Fraction
        """
        numerical_coordinate_data = []
        for coordinate_index in raw_coordinate_array:
            if isinstance(coordinate_index, dict):
                # Might be an unsupported data type; just let the error pass up if so
                coordinate_index_value = parse_fraction_from_dict(coordinate_index)
            elif isinstance(coordinate_index, (str, unicode)):
                if '/' in coordinate_index: # is a fraction
                    coordinate_index_value = Fraction(coordinate_index)
                elif '.' in coordinate_index_value: # is a float
                    coordinate_index_value = float(coordinate_index_value)
                elif coordinate_index.isnumeric(): # is an int
                    # interpret all ints as fractions so that we can do division if need be
                    coordinate_index_value = Fraction(coordinate_index_value)
                else:
                    raise RuntimeError('Unexpected string '+coordinate_index+\
                    'encountered while parsing atom coordinates: '+str(raw_coordinate_array))
            elif isinstance(coordinate_index, (int, float, Fraction)):
                coordinate_index_value = coordinate_index
            else:
                try:
                    coordinate_index_value = float(coordinate_index)
                except Exception:
                    raise RuntimeError('Unexpected data type '+str(type(coordinate_index))+\
                        'encountered while parsing atom coordinates: '+str(raw_coordinate_array))
            numerical_coordinate_data.append(coordinate_index_value)
        return numerical_coordinate_data

class SimpleObjectJSONEncoder(JSONEncoder):
    """Encodes objects into JSON using their __dict__ form"""
    def default(self, o):
        """Encodes the object o using o.__dict___"""
        if isinstance(o,Fraction):
            return {"_type":"fraction", "numerator":o.numerator, "denominator":o.denominator}
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
    """
    Represents a single direct input value for Abinit.

    Each attribute has the following format:

    {
        "name": <string>,
        "value": <input value>,
        "comment": <string, optional>
    }
    or
    {
        "comment": <string>
    }

    Additional properties are ignored.

    Input values may be the following types:

    literal (string or number):
        placed as-is
    array of literals:
        placed in-line, separated by 2 spaces
    matrix of literals:
        placed on each line after the label,
        indented with values separated by 2 spaces
    fraction:
        a JSON object with '_type':'fraction'
        and either literal 'numerator' and 'denominator' fields
        or a 'value':'A/B' field
    """
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
                return parse_fraction_from_dict(element)
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

def parse_fraction_from_dict(fraction_dict):
    """
    Accepts a dict object and returns a Fraction that represents the same data.
    The following formats are supported:

    numerator, denominator (as anything castable to an int)
    value="A/B"
    """
    if 'numerator' in fraction_dict and 'denominator' in fraction_dict:
        return Fraction(int(fraction_dict['numerator']), int(fraction_dict['denominator']))
    elif 'value' in fraction_dict:
        return Fraction(fraction_dict['value'])
    raise NotImplementedError("Unknown Fraction format: "+fraction_dict)


class Atom:
    """A simple attribute representing an Atom with a position"""
    def __init__(self, znucl, coord):
        self.znucl = znucl
        # if not (isinstance(coord, Coordinate) and coord.coordinate_system == "reduced"):
        #     raise RuntimeError("Coordinate "+coord+" must be a Coordinate in the reduced system")
        if isinstance(coord, Coordinate):
            self.coord = coord #assumed to be a Coordinate object in the "reduced" system
        else:
            self.coord = Coordinate(coord, "reduced")

    def __repr__(self):
        """Return a string representing this atom in JSON"""
        return {"znucl":self.znucl, "coord":self.coord.coordinate_array}.__repr__()

    def __eq__(self, other):
        """Returns true if other is an Atom with the equal znucl and coord"""
        return isinstance(other, Atom)\
            and self.znucl == other.znucl\
            and self.coord == other.coord

    def __hash__(self):
        """Returns a unique hash on this object based on the znucl and coord"""
        return hash((self.znucl, self.coord))

def parse_atoms(atoms_json_array):
    """Gets a list of AtomAttributes from the JSON of an experiment describing atomic positions"""
    if atoms_json_array is None:
        raise RuntimeError("Tried to parse the experiment's metadata for an atoms attribute, but could not find it.")
    else:
        return [parse_atom_attribute_from_dict(attr) for attr in atoms_json_array]

def parse_atom_attribute_from_dict(atom_attribute_dict):
    """Takes a dict parsed from a JSON dict and returns an Atom representing the same data."""
    if isinstance(atom_attribute_dict['coord'], dict):
        fractional_coordinate = Coordinate(\
            coordinate_array=atom_attribute_dict['coord']['coordinate_array'], \
            coordinate_system=atom_attribute_dict['coord'].get('coordinate_system', "reduced"))
    else:
        fractional_coordinate = \
            Coordinate(coordinate_array=atom_attribute_dict['coord'],coordinate_system="reduced")
    return Atom( \
        int(atom_attribute_dict['znucl']), fractional_coordinate)

class Experiment:
    """
    A class representing a single Abinit experiment.

    Every experiment has an array of SimpleAttributes "direct" and a dictionary of named meta-values "meta".
    """
    def __init__(self, direct=None, meta=None):
        self.direct = direct
        self.meta = meta

    def __repr__(self, indent=None):
        """
        Represents this Experiment in JSON format
        Can specify indentation via indent parameter
        """
        return json.dumps(self.__dict__, cls=SimpleObjectJSONEncoder, indent=indent)

    def compile(self):
        """
        Represents this Experiment as an ABINIT input file.
        Each direct attribute is represented on separate lines,
        with associated comments preceding labels.
        Meta values are ignored.
        Returns a native python string; it's recommended to .encode("UTF-8") the result.
        """
        return "\n\n".join([attribute.__str__() for attribute in self.direct])

    def get_direct_property(self, property_name):
        """Returns the first direct property with the same name as property_name"""
        return [prop for prop in self.direct if prop.name == property_name][0]

    @staticmethod
    def load_from_json_file(fp, cls=SimpleAttributeJSONDecoder):
        """
        Returns an Experiment loaded from JSON in the given file pointer
        By default, uses SimpleAttributeJSONDecoder as the cls for loading JSON,
        which means that everything in "meta" will just be a simple dict
        """
        input_data = json.load(fp, cls=cls)
        return Experiment(direct=input_data.get('direct', []), meta=input_data.get('meta', {}))

atomic_names = [(0, '-', 'DUMMY'),
                (1, 'H', 'Hydrogen'),
                (2, 'He', 'Helium'),
                (3, 'Li', 'Lithium'),
                (4, 'Be', 'Beryllium'),
                (5, 'B', 'Boron'),
                (6, 'C', 'Carbon'),
                (7, 'N', 'Nitrogen'),
                (8, 'O', 'Oxygen'),
                (9, 'F', 'Fluorine'),
                (10, 'Ne', 'Neon'),
                (11, 'Na', 'Sodium'),
                (12, 'Mg', 'Magnesium'),
                (13, 'Al', 'Aluminum'),
                (14, 'Si', 'Silicon'),
                (15, 'P', 'Phosphorus'),
                (16, 'S', 'Sulfur'),
                (17, 'Cl', 'Chlorine'),
                (18, 'Ar', 'Argon'),
                (19, 'K', 'Potassium'),
                (20, 'Ca', 'Calcium'),
                (21, 'Sc', 'Scandium'),
                (22, 'Ti', 'Titanium'),
                (23, 'V', 'Vanadium'),
                (24, 'Cr', 'Chromium'),
                (25, 'Mn', 'Manganese'),
                (26, 'Fe', 'Iron'),
                (27, 'Co', 'Cobalt'),
                (28, 'Ni', 'Nickel'),
                (29, 'Cu', 'Copper'),
                (30, 'Zn', 'Zinc'),
                (31, 'Ga', 'Gallium'),
                (32, 'Ge', 'Germanium'),
                (33, 'As', 'Arsenic'),
                (34, 'Se', 'Selenium'),
                (35, 'Br', 'Bromine'),
                (36, 'Kr', 'Krypton'),
                (37, 'Rb', 'Rubidium'),
                (38, 'Sr', 'Strontium'),
                (39, 'Y', 'Yttrium'),
                (40, 'Zr', 'Zirconium'),
                (41, 'Nb', 'Niobium'),
                (42, 'Mo', 'Molybdenum'),
                (43, 'Tc', 'Technetium'),
                (44, 'Ru', 'Ruthenium'),
                (45, 'Rh', 'Rhodium'),
                (46, 'Pd', 'Palladium'),
                (47, 'Ag', 'Silver'),
                (48, 'Cd', 'Cadmium'),
                (49, 'In', 'Indium'),
                (50, 'Sn', 'Tin'),
                (51, 'Sb', 'Antimony'),
                (52, 'Te', 'Tellurium'),
                (53, 'I', 'Iodine'),
                (54, 'Xe', 'Xenon'),
                (55, 'Cs', 'Cesium'),
                (56, 'Ba', 'Barium'),
                (57, 'La', 'Lanthanum'),
                (58, 'Ce', 'Cerium'),
                (59, 'Pr', 'Praseodymium'),
                (60, 'Nd', 'Neodymium'),
                (61, 'Pm', 'Promethium'),
                (62, 'Sm', 'Samarium'),
                (63, 'Eu', 'Europium'),
                (64, 'Gd', 'Gadolinium'),
                (65, 'Tb', 'Terbium'),
                (66, 'Dy', 'Dysprosium'),
                (67, 'Ho', 'Holmium'),
                (68, 'Er', 'Erbium'),
                (69, 'Tm', 'Thulium'),
                (70, 'Yb', 'Ytterbium'),
                (71, 'Lu', 'Lutetium'),
                (72, 'Hf', 'Hafnium'),
                (73, 'Ta', 'Tantalum'),
                (74, 'W', 'Tungsten'),
                (75, 'Re', 'Rhenium'),
                (76, 'Os', 'Osmium'),
                (77, 'Ir', 'Iridium'),
                (78, 'Pt', 'Platinum'),
                (79, 'Au', 'Gold'),
                (80, 'Hg', 'Mercury'),
                (81, 'Tl', 'Thallium'),
                (82, 'Pb', 'Lead'),
                (83, 'Bi', 'Bismuth'),
                (84, 'Po', 'Polonium'),
                (85, 'At', 'Astatine'),
                (86, 'Rn', 'Radon'),
                (87, 'Fr', 'Francium'),
                (88, 'Ra', 'Radium'),
                (89, 'Ac', 'Actinium'),
                (90, 'Th', 'Thorium'),
                (91, 'Pa', 'Protactinium'),
                (92, 'U', 'Uranium'),
                (93, 'Np', 'Neptunium'),
                (94, 'Pu', 'Plutonium'),
                (95, 'Am', 'Americium'),
                (96, 'Cm', 'Curium'),
                (97, 'Bk', 'Berkelium'),
                (98, 'Cf', 'Californium'),
                (99, 'Es', 'Einsteinium'),
                (100, 'Fm', 'Fermium'),
                (101, 'Md', 'Mendelevium'),
                (102, 'No', 'Nobelium'),
                (103, 'Lr', 'Lawrencium'),
                (104, 'Rf', 'Rutherfordium'),
                (105, 'Db', 'Dubnium'),
                (106, 'Sg', 'Seaborgium'),
                (107, 'Bh', 'Bohrium'),
                (108, 'Hs', 'Hassium'),
                (109, 'Mt', 'Meitnerium'),
                (110, 'Ds', 'Darmstadtium'),
                (111, 'Rg', 'Roentgenium'),
                (112, 'Cn', 'Copernicium'),
                (113, 'Nh', 'Nihonium'),
                (114, 'Fl', 'Flerovium'),
                (115, 'Mc', 'Moscovium'),
                (116, 'Lv', 'Livermorium'),
                (117, 'Ts', 'Tennessine'),
                (118, 'Og', 'Oganesson')]

def get_atomic_symbol(atomic_number):
    """returns the symbol of the atom with the given atomic number"""
    return atomic_names[atomic_number][1] # remember, python

def get_atomic_number(atomic_symbol):
    """Returns the first element with the same symbol as listed"""
    return [element[0] for element in element_names if element[1] == element_symbol][0]