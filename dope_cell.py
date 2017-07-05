#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit,
determines positions of atoms from the "meta.atoms" data,
dopes the cell according to the "meta.dopings[]" data,
and outputs a new json file to stdout.

This input format is indicated by the .abinit.json format.
See 'generate_abinit_input_file_from_json.py' for details.

The struture of the relevant meta-attributes are as follows:

{
    "direct": [ ... ],
    "meta": {
        ...
        "atoms" : [
            <atoms attributes>
        ],
        ...
        "dopings": [
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

Any atom matching the coordinates of an atom in "meta.dopings[]" will be modified
to have the doped "znucl" value of the matching atom.

If an atom in "meta.dopings[]" is not used, an error is raised.
"""


__version__ = "0.0.0"

__author__ = "JJ Brown"
__copyright__ = "Copyright 2017, JJ Brown"
__credits__ = ["JJ Brown"]
__license__ = "MIT"
__maintainer__ = "JJ Brown"
__status__ = "development"

import json
import handle_command_line_IO
import sys
from abinit_data_types import parse_atoms, SimpleObjectJSONEncoder, Experiment

GENERATED_VALUE_COMMENT = "This field was automatically generated"

def display_help_message():
    """Prints a help message with usage instructions to stderr"""
    handle_command_line_IO.errprint("Usage: python convert_abinit_input_from_atoms_to_direct.py [infile.abinit.json] > [outfile.abinit.json]")

def dope_atoms(atoms_list, doping_atoms_list):
    """
    Given a list of atoms within a unit cell (coordinates from 0 to 1),
    MUTATES that list of atoms by doping them according to doping_atoms_list,
    and then returns the modified list
    """

    #copy in each direction, preserving atom order
    for doping_atom in doping_atoms_list:
        successfully_doped_atom = False
        for atom in atoms_list:
            if atom.coord == doping_atom.coord:
                atom.znucl = doping_atom.znucl
                successfully_doped_atom = True
                break #just the inner loop, so we don't have to keep checking atoms
        if not successfully_doped_atom:
            raise RuntimeError( \
                "Cannot find an atom with the same coordinates as " \
                + str(doping_atom) \
                + "\nDoping pattern must match the underlying cell")

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
        if experiment.meta and 'dopings' in experiment.meta and 'atoms' in experiment.meta:

            # Get the atoms and dopings, remove the dopings
            experiment.meta['atoms'] = \
                dope_atoms(\
                    parse_atoms(experiment.meta['atoms']),\
                    parse_atoms(experiment.meta.pop('dopings', None)) \
                    )
        else:
            handle_command_line_IO.errprint("No doping of unit cell specified; taking no action")

        # Echo the resulting experiment back to stdout
        print json.dumps(experiment, cls=SimpleObjectJSONEncoder, indent=4)

if __name__ == '__main__':
    main()
