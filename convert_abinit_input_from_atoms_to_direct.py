#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit,
determines positions of atoms from the "meta" data,
and outputs a new json file with direct settings to stdout.

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

The data describing the atoms will be output to the following fields:
natom, ntypat, typat, znucl, xred
Any data already in these fields will overwritten.

For now, it is always assumed that the coordinates are specified by their
fractional position within the cell, for the xred field.
"""


__version__ = "0.0.0"

__author__ = "JJ Brown"
__copyright__ = "Copyright 2017, JJ Brown"
__credits__ = ["JJ Brown"]
__license__ = "MIT"
__maintainer__ = "JJ Brown"
__status__ = "development"

from OrderedSet import OrderedSet
from abinit_data_types import get_atoms_from_experiment_meta_data,SimpleAttribute,SimpleAttributeJSONDecoder,SimpleObjectJSONEncoder
import json
import handle_command_line_IO
import sys

GENERATED_VALUE_COMMENT = "This field was automatically generated"

def display_help_message():
	"""Prints a help message with usage instructions to stderr"""
	handle_command_line_IO.errprint("Usage: python convert_abinit_input_from_atoms_to_direct.py [infile.abinit.json] > [outfile.abinit.json]")

input_file,_ = handle_command_line_IO.get_input_file(display_help_message) # get from stdin or first argument's file
input_data = json.load(input_file, cls=SimpleAttributeJSONDecoder)

if('meta' in input_data and 'atoms' in input_data['meta']): #allow for pass-through if there's nothing to do
	atoms = sorted(get_atoms_from_experiment_meta_data(input_data),key=lambda atom: atom.znucl) # sorted so we can group by znucl
	input_data['meta']['atoms'] = None
	atom_types = OrderedSet([atom.znucl for atom in atoms])
	znucl_to_typat_mapping = dict((znucl,index+1) for index,znucl in enumerate(atom_types))

	input_data['direct'].append(SimpleAttribute(name="natom", value=len(atoms), comment=GENERATED_VALUE_COMMENT))
	input_data['direct'].append(SimpleAttribute(name="ntypat", value=len(atom_types), comment=GENERATED_VALUE_COMMENT))
	input_data['direct'].append(SimpleAttribute(name="znucl", value=list(atom_types), comment=GENERATED_VALUE_COMMENT))
	input_data['direct'].append(SimpleAttribute(name="typat", value=[znucl_to_typat_mapping[atom.znucl] for atom in atoms], comment=GENERATED_VALUE_COMMENT))
	input_data['direct'].append(SimpleAttribute(name="xred"	, value=[atom.coord.coordinate_array for atom in atoms], comment=GENERATED_VALUE_COMMENT))

print json.dumps(input_data, cls=SimpleObjectJSONEncoder, indent=4) 
