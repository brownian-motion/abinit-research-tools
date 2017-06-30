#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit,
determines positions of atoms from the "meta.atoms" data,
copies the cell according to the "meta.repeat_cell" data,
and outputs a new json file with direct settings to stdout.

Atoms are repeated in each cardinal direction in 3-D space according to the "meta.repeat_cell" property.
If this is a scalar, atoms are repeated in all 3 directions; if it is an array,
they are repeated nx, ny, nz times in each direction. For example, if "meta.repeat_cell"
has the value [2, 4, 1], then the unit cell is doubled in the x direction,
quadrupled in the y direction, and kept the same in the z direction.
All "meta.repeat_cell" values must be integers.

Note that the values of "direct.acell" will also be modified by this script.

This input format is indicated by the .abinit.json format.
See 'generate_abinit_input_file_from_json.py' for details.

Atoms are specified using the 'atoms' attribute within 'meta', like so:

{
    "direct": [ ... ],
    "meta": {
        ...
        "atoms" : [
            <atoms attributes>
        ]
    }
}

Each atom is specified in the following way:
{
    "znucl":<nuclear charge:int>,
    "coord":<coordinate>
}

See 'convert_abinit_input_from_atoms_to_direct.py' for more details.
"""


__version__ = "0.0.0"

__author__ = "JJ Brown"
__copyright__ = "Copyright 2017, JJ Brown"
__credits__ = ["JJ Brown"]
__license__ = "MIT"
__maintainer__ = "JJ Brown"
__status__ = "development"

from OrderedSet import OrderedSet
import json
import handle_command_line_IO
import sys
from fractions import Fraction
from itertools import islice
from abinit_data_types import parse_atoms, SimpleAttribute, SimpleObjectJSONEncoder, Experiment, Atom, Coordinate

GENERATED_VALUE_COMMENT = "This field was automatically generated"

def display_help_message():
    """Prints a help message with usage instructions to stderr"""
    handle_command_line_IO.errprint("Usage: python convert_abinit_input_from_atoms_to_direct.py [infile.abinit.json] > [outfile.abinit.json]")

def repeat_atoms_in_unit_cell(atoms_list, repeat_factor_3d):
    """
    Given a list of atoms within a unit cell (coordinates from 0 to 1),
    MUTATES that list of atoms by repeating them in each direction by repeat_factor_3d,
    also within the unit cell (Coordinates are scaled down),
    and then returns the modified list
    """
    if 0 in repeat_factor_3d:
        return []

    #scale down the unit cell
    atoms_list = [Atom(atom.znucl, atom.coord / repeat_factor_3d) for atom in atoms_list]
    original_cell_size = Coordinate(coordinate_array=[Fraction(1,x) for x in repeat_factor_3d])

    #copy in each direction, preserving atom order
    for cardinal_direction_index in xrange(0, 3):
        num_original_atoms = len(atoms_list)
        scale_factor_vector = [0, 0, 0]
        #skip 0, it already exists
        for repitition_number in xrange(1, repeat_factor_3d[cardinal_direction_index]):
            scale_factor_vector[cardinal_direction_index] = repitition_number
            for atom in islice(atoms_list, num_original_atoms):
                atoms_list.append(Atom(atom.znucl, atom.coord + original_cell_size * scale_factor_vector))
    return atoms_list

def main():
    """
    Reads an experiment .abinit.json from stdin or from the file marked in the first argument,
    and copies the unit cell in each cardinal direction according to the value
    in "meta.repeat_cell", modifiying "meta.atoms" and "direct.acell".
    Outputs in .abinit.json format to stdout.
    """
    # Get input from stdin or first argument's file
    with handle_command_line_IO.get_input_file(display_help_message) as input_file:
        experiment = Experiment.load_from_json_file(input_file)

        # Make this transparent; if no scaling is specified, don't scale
        if experiment.meta and 'repeat_cell' in experiment.meta and 'atoms' in experiment.meta:
            # Get the number of times to repeat
            repeat_factor = experiment.meta['repeat_cell']
            if isinstance(repeat_factor, list):
                if len(repeat_factor) != 3:
                    raise RuntimeError("Unit cell must be 3-D.")
            else:
                # if this throws an error, just report it to the user
                repeat_factor = [int(repeat_factor)] * 3

            # Repeat the atoms
            experiment.meta['atoms'] = \
                repeat_atoms_in_unit_cell(parse_atoms(experiment.meta['atoms']), repeat_factor)

            # Scale the unit cell
            for attribute in experiment.direct:
                if attribute.name == "acell":
                    attribute.value = [attribute.value[i] * repeat_factor[i] for i in xrange(0, 3)]

            # Take out repetition of cell so it doesn't happen again somehow
            experiment.meta['repeat_cell'] = None
        else:
            handle_command_line_IO.errprint("No repeat of unit cell specified; taking no action")

        # Echo the resulting experiment back to stdout
        print json.dumps(experiment, cls=SimpleObjectJSONEncoder, indent=4)

if __name__ == '__main__':
    main()
