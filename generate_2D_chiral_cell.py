#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit,
determines positions of atoms from the "meta.atoms" data,
rotates and repeats the cell according to the "meta.make_chirality" data,
and outputs a new json file with direct settings to stdout.

Atoms are repeated in each cardinal direction in 3-D space according to the "meta.make_chirality" property.
Any axes not provided with a desired chirality are assumed to be 0.
For example, if "meta.make_chirality" has the value [2, 1, 0], then the unit cell
is rotated and repeated so that (1,0,0) becomes (2,1,0), (0,1,0) becomes (-1,2,0), and
(0,0,1) stays (0,0,1).
All "meta.make_chirality" values must be integers.

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

import json
from math import sin, cos, atan2
import handle_command_line_IO
from abinit_data_types import parse_atoms, SimpleObjectJSONEncoder, Experiment, Atom, Coordinate
from repeat_atoms_in_cell import repeat_atoms_in_unit_cell

GENERATED_VALUE_COMMENT = "This field was automatically generated"

def display_help_message():
    """Prints a help message with usage instructions to stderr"""
    handle_command_line_IO.errprint("Usage: python convert_abinit_input_from_atoms_to_direct.py"\
        +" [infile.abinit.json] > [outfile.abinit.json]")



def generate_xy_chiral_cell(unit_cell_atoms_list, desired_chirality):
    """
    Given a list of atoms within a unit cell (coordinates from 0 to 1),
    creates a larger chiral cell of that atom grid,
    such that (1,0,0) -> ( desired_cirality[0], desired_chirality[1], 0) / |desired_chirality|
    and       (0,1,0) -> (-desired_cirality[1], desired_chirality[0], 0) / |desired_chirality|
    and then returns that list.

    This is performed by repeating the existing the original unit cell
    until it's larger than the size of the desired unit cell in any rotation,
    rotating the coordinates of all atoms,
    filtering out all atoms not in the new unit cell,
    and returning the resulting array.

    This algorithm only supports chiralities of dimension 2.

    It is terribly memory inefficient, but that's not a big concern.
    """
    assert len(desired_chirality) == 2 or desired_chirality[2] == 0

    sum_of_chirality = sum(desired_chirality)

    xy_angle_to_rotate = -atan2(desired_chirality[1], desired_chirality[0])

    repeated_atoms = [Atom(atom.znucl, atom.coord + [a1, a2, 0])
                      for a1 in xrange(-sum_of_chirality, sum_of_chirality)
                      for a2 in xrange(-sum_of_chirality, sum_of_chirality)
                      for atom in unit_cell_atoms_list]

    rotated_atoms = \
    [Atom(atom.znucl, rotate_coordinate_around_z_axis(atom.coord, xy_angle_to_rotate)) \
        for atom in repeated_atoms]

    ## Accounts for shrinking of unit cell by repeat_atoms_in_unit_cell
    normalization_factor = 1/(desired_chirality[0] ** 2 + desired_chirality[1] ** 2) ** 0.5

    normalization_vector = [normalization_factor, normalization_factor, 1]

    normalized_atoms =\
        [Atom(atom.znucl, atom.coord*normalization_vector)\
            for atom in rotated_atoms]

    return [atom for atom in normalized_atoms if is_inside_unit_cell(atom.coord)]

def is_inside_unit_cell(coordinate):
    """Returns True if the coordinate is in the unit cell between 0 and 1, excluding 1"""
    return coordinate.coordinate_array[0] >= 0 \
           and coordinate.coordinate_array[0] < 1 \
           and coordinate.coordinate_array[1] >= 0 \
           and coordinate.coordinate_array[1] < 1 \
           and coordinate.coordinate_array[2] >= 0 \
           and coordinate.coordinate_array[2] < 1

def modulo_to_unit_cell(coordinate):
    """Returns a new Coordinate with values modulo-d onto the unit cell (coord%1)"""
    return Coordinate(\
        coordinate_array=[(val % 1) for val in coordinate.coordinate_array],
        coordinate_system=coordinate.coordinate_system)

def rotate_coordinate_around_z_axis(coordinate, angle):
    """Returns a new Coordinate rotated in the x-y plane by the given angle"""
    return Coordinate(
        coordinate_array=[
            coordinate.coordinate_array[0] * cos(angle) - coordinate.coordinate_array[1] * sin(angle),
            coordinate.coordinate_array[0] * sin(angle) + coordinate.coordinate_array[1] * cos(angle),
            coordinate.coordinate_array[2]],
        coordinate_system=coordinate.coordinate_system)

def main():
    """
    Reads an experiment .abinit.json from stdin or from the file marked in the first argument,
    and generates a 2-D chiral tesselation of the cell according to the values in
    in "meta.make_chirality", modifiying "meta.atoms" and "direct.acell".
    Outputs in .abinit.json format to stdout.
    """
    # Get input from stdin or first argument's file
    with handle_command_line_IO.get_input_file(display_help_message) as input_file:
        experiment = Experiment.load_from_json_file(input_file)

        # Make this transparent; if no scaling is specified, don't scale
        if experiment.meta and 'make_chirality' in experiment.meta and 'atoms' in experiment.meta:
            # Get the number of times to repeat
            desired_chirality = experiment.meta.pop('make_chirality', None)
            if not isinstance(desired_chirality, list) or len(desired_chirality) != 2:
                raise RuntimeError("Desired chirality must be 2-D.")

            # Repeat the atoms
            experiment.meta['atoms'] = \
                generate_xy_chiral_cell(parse_atoms(experiment.meta['atoms']), desired_chirality)

            # Scale the unit cell
            normalization_factor = (desired_chirality[0] ** 2 + desired_chirality[1] ** 2) ** 0.5
            for attribute in experiment.direct:
                if attribute.name == "acell":
                    attribute.value = \
                        [attribute.value[0] * normalization_factor, \
                         attribute.value[1] * normalization_factor, \
                         attribute.value[2]]
        else:
            handle_command_line_IO.errprint("No chirality of unit cell specified; taking no action")

        # Echo the resulting experiment back to stdout
        print json.dumps(experiment, cls=SimpleObjectJSONEncoder, indent=4)

if __name__ == '__main__':
    main()
