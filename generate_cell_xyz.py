#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit,
determines positions of atoms within a unit cell from the "meta.atoms" data,
positions those atoms in a 60° rhombus unit cell,
and outputs the result in XYZ format.

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

import handle_command_line_IO
from abinit_data_types import parse_atoms, Experiment, Atom
from manipulate_cell import get_rhombal_cell

def repr_in_xyz(atom):
    """Returns a single line representing the position of the given atom for a .xyz file"""
    return str(atom.znucl)+' '+' '.join([str(val) for val in atom.coord.coordinate_array])

def main():
    """
    Displays the atoms from the meta attributes of the input experiment within a rhombal unit cell
    """
    with handle_command_line_IO.get_input_file(display_help_function) as input_file:
        experiment = Experiment.load_from_json_file(input_file)
        atoms = parse_atoms(experiment.meta['atoms'])
        rhomb_atoms = get_rhombal_cell(atoms)
        acell_raw = experiment.get_direct_property('acell')
        cell_size = [float(coord) for coord in acell_raw.value]
        correct_size_rhomb_atoms = [Atom(atom.znucl, atom.coord*cell_size) for atom in rhomb_atoms]
        print len(atoms)
        print '' #no comment on the file
        for atom in correct_size_rhomb_atoms:
            print repr_in_xyz(atom)

def display_help_function():
    """
    displays usage information for this file
    """
    handle_command_line_IO.errprint(\
    	'Usage: [echo input_file.abinit.json | ] '+\
    	'python generate_cell_xyz_rhombus.py [input_file.abinit.json]')

if __name__ == '__main__':
    main()
