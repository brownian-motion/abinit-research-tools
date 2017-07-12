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
from abinit_data_types import parse_atoms, Experiment, Atom, get_atomic_symbol
from manipulate_cell import get_rhombal_cell

def repr_single_atom_in_cif(atom):
    """Returns a single line representing the position of the given atom for a .cif file"""
    return " " + get_atomic_symbol(atom.znucl) + "  " + " ".join([str(coord) for coord in atom.coord.coordinate_array])

def repr_atoms_in_cif(atoms):
    """returns the _loop section of a .cif file representing atom positions"""
    return "loop_\n"+\
        "\n".join(["_atom_site_type_symbol", "_atom_site_fract_x", "_atom_site_fract_y", "_atom_site_fract_z"])+"\n"+\
        "\n".join([repr_single_atom_in_cif(atom) for atom in atoms])

def repr_acell_property_in_cif(acell):
    """represents the size of the unit cell in .cif format, given a list of cell lengths"""
    return "_cell_length_a "+str(acell[0])\
           +"\n_cell_length_b "+str(acell[1])\
           +"\n_cell_length_c "+str(acell[2])

def repr_angdeg_property_in_cif(angdeg):
    """represents the angles of the unit cell in .cif format, given a list of cell angles"""
    return "_cell_angle_alpha "+str(angdeg[0])\
           +"\n_cell_angle_beta "+str(angdeg[1])\
           +"\n_cell_angle_gamma "+str(angdeg[2])

def repr_experiment_in_cif(experiment):
    """represents the entire experiment in .cif format"""
    return "\n".join([\
        repr_angdeg_property_in_cif(experiment.get_direct_property('angdeg').value),
        repr_acell_property_in_cif(experiment.get_direct_property('acell').value),
        repr_atoms_in_cif(parse_atoms(experiment.meta['atoms']))\
        ])

def main():
    """
    Displays the atoms from the meta attributes of the input experiment within a rhombal unit cell
    """
    with handle_command_line_IO.get_input_file(display_help_function) as input_file:
        print repr_experiment_in_cif(Experiment.load_from_json_file(input_file))

def display_help_function():
    """
    displays usage information for this file
    """
    handle_command_line_IO.errprint(\
        'Usage: [echo input_file.abinit.json | ] '+\
    	'python generate_cell_xyz_rhombus.py [input_file.abinit.json]')

if __name__ == '__main__':
    main()
