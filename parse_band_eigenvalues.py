#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""Parses an input file from Abinit describing eigenenergies of a simulation, and outputs it as JSON to stdout"""

__version__ = "0.0.0"

__author__ = "JJ Brown"
__copyright__ = "Copyright 2017, JJ Brown"
__credits__ = ["JJ Brown"]
__license__ = "MIT"
__maintainer__ = "JJ Brown"
__status__ = "development"

import string
import json
from abinit_data_types import Coordinate, KPointWithEnergy, SimpleObjectJSONEncoder
import handle_command_line_IO

def parse_band_eigenenergy_file(file_handler):
    """ The main workhorse of this program.
    Parses the given file with eigenenergy information from Abinit
    The file format is as follows, with variables in <>:
        Eigenvalues ( <energy_unit> ) for nkpt= <num_k_points> k points:
        <k points>
    Each k point is described on two lines, as follows
        kpt#    <number>, nband=    <num_bands>, wtk=    <wtk>, kpt=  <x1> <x2> <x3> (<coord system>)
        <band1_energy>  <band2_energy> ...

    This function returns an array of KPointWithEnergy objects
    """
    first_line = file_handler.readline()
    num_k_points, energy_unit = parse_num_k_points_and_energy_unit_from_first_line(first_line)
    k_points = []
    for k_point in xrange(1, num_k_points+1): # +1 because range and xrange have exlusive maxes
        line_one = file_handler.readline()
        number, num_bands, wtk, coord = parse_k_point_line_one_for_number_nband_wtk_coord(line_one)
        assert number == k_point
        band_energies = []
        while len(band_energies) < num_bands:
            band_energies.extend(parse_line_for_k_point_band_energies(file_handler.readline()))
        k_points.append(KPointWithEnergy(number, num_bands, wtk, coord, band_energies, energy_unit))
    handle_command_line_IO.errprint(k_points)
    return k_points

def parse_num_k_points_and_energy_unit_from_first_line(first_line): #works!
    """
    Accepts the text of the first line from an Abinit band eigenergy file and extracts the number
    of k-points and the unit for energy used in the file.
    Returns a tuple in the form <n k points:int>,<energy unit:string>
    """
    words = string.split(first_line)
    return int(words[6]), words[2]

def parse_line_for_k_point_band_energies(second_line):
    """
    Parses a line describing the eigenvalues of a k-point.
    Given a string describing energies in scientific notation separated by spaces,
    returns an array of those energies as floats.
    """
    return map(float, string.split(second_line))

def parse_k_point_line_one_for_number_nband_wtk_coord(line_one):
    """
    Parses the second line describing the eigenvalues of a k-point.
    Given a string with the format
        kpt#    <number>, nband=    <num_bands>, wtk=    <wtk>, kpt=  <x1> <x2> <x3> (<coord_system>)
    returns the values
        number:int, num_bands:int, wtk:float, Coordinate([x1:float, x2:float, x3:float], coord_system:str)
    """
    words = line_one.split()

    coordinate_system = line_one[line_one.rfind('(')+1:-2]
    coordinate = Coordinate([float(words[7]), float(words[8]), float(words[9])], coordinate_system)
    return \
        int(words[1].strip(',')), \
        int(words[3].strip(',')), \
        float(words[5].strip(',')), \
        coordinate

def err_print_help_message():
    """Prints a short help message describing how to use this program"""
    handle_command_line_IO.errprint("Usage: parse_band_eigenvalues.py <filename>")

def main():
    """
    Accepts input on stdin or from the file specified in the first argument,
    reads band eigenenergy data output from ABINIT,
    and outputs a JSON file representing the data in JSON.
    """
    with handle_command_line_IO.get_input_file(err_print_help_message) as input_file:
        print json.dumps(parse_band_eigenenergy_file(input_file), cls=SimpleObjectJSONEncoder)

if __name__ == '__main__':
    main()
