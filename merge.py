#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Parses a list of json files of input settings for Abinit,
receiving (optionally) from stdin and from files specified by the arguments,
merges those experiment settings together,
and outputs a new single json file with direct settings to stdout.

This input format is indicated by the .abinit.json format.
See 'generate_abinit_input_file_from_json.py' for details.
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
    handle_command_line_IO.errprint("Usage: [cat input1.abinit.json | ] python merge.py [input2.abinit.json ... ] > [outfile.abinit.json]")

def experiment_union(experiment_one, experiment_two, collision_resolution='raise'):
    """
    Returns a new Experiment representing the union of settings specified in the two given Experiments.
    Direct settings are merged using union of lists,
    while meta settings are merged by creating a dict with the settings specified in both.
    The behavior when two experiments specify the same setting
    can be changed with the 'collision_resolution' parameter:
        'raise' (Default) : raise a RuntimeError if the same setting is 
                            specified in both experiments
        'keep_original'   : keep the setting specified in the first colliding experiment,
                            and discard the rest
        'overwrite'        : keep the setting specified in the last colliding experiment,
                            and discard the rest
    """
    result_meta = dict(experiment_one.meta or {}) #shallow copy - fine bc we won't edit deeply
    if experiment_two.meta:
        for key in experiment_two.meta:
            if key in result_meta:
                if collision_resolution == 'keep_original':
                    pass
                elif collision_resolution == 'overwrite':
                    result_meta[key] = experiment_two.meta[key]
                else: # collision_resolution == 'raise':
                    raise RuntimeError('Meta setting '+key+' is specified in two experiments')
            else:
                result_meta[key] = experiment_two.meta[key]
    return Experiment(direct=(experiment_one.direct or [])+(experiment_two.direct or []), meta=result_meta)

def main():
    """
    Reads an experiment .abinit.json from stdin or from the file marked in the first argument,
    and copies the unit cell in each cardinal direction according to the value
    in "meta.repeat_cell", modifiying "meta.atoms" and "direct.acell".
    Outputs in .abinit.json format to stdout.
    """
    # Get input from stdin or first argument's file
    input_file, other_file_names = \
        handle_command_line_IO.get_input_file_and_args(display_help_message)
    with input_file:
        experiment = Experiment.load_from_json_file(input_file)

        # Get all of the other specified input files
        for file_name in other_file_names:
            with open(file_name, "r") as next_file:
                next_experiment = Experiment.load_from_json_file(next_file)
                experiment = experiment_union(experiment, next_experiment)

        # Echo the resulting experiment back to stdout
        print json.dumps(experiment, cls=SimpleObjectJSONEncoder, indent=4)

if __name__ == '__main__':
    main()
