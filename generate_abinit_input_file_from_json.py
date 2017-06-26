#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses an json file of input settings for Abinit, and outputs an Abinit input file to stdout.

This input format is indicated by the .abinit.json format.

The format supported is as follows:

{
	"direct": // an array of attributes to put directly into Abinit
	[
		<attributes>
	],

	"meta": // a dictionary of values describing the input, that may be used to create input but are not input directly
	{
		<meta-atribute name>:<pretty much anything>
	}
}

Each attribute has some combination of the following fields:

{
	"name": <string>,
	"value": <input value>,
	"comment": <string>
}

For "direct" data, all attributes must have either a name/value and an optional comment,
or just a comment.
Additional properties are ignored.

For "meta" data, values may be anything.
This is to allow high customization of experiments.
This program does not parse meta data.

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

This file ignores all "meta" attributes and naively places all "direct" attributes,
with comments for each input preceding each input.
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
import abinit_data_types

def display_help_message():
	"""Prints a help message with usage instructions to stderr"""
	handle_command_line_IO.errprint("Usage: python generate_abinit_input_file_from_json.py [filename.abinit.json] > outputfile.in")

input_file,_ = handle_command_line_IO.get_input_file(display_help_message) # get from stdin or first argument's file
input_data = json.load(input_file, cls=abinit_data_types.SimpleAttributeJSONDecoder)
print("\n\n".join([attribute.__str__() for attribute in input_data[u'direct']]).encode("UTF-8")) # send to stdout for redirection