#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""
Used to handle bulk manipulations of entire lists of Atom objects representing a crystal unit cell
"""

from math import acos, sqrt, sin, cos
import numpy
from abinit_data_types import Atom, Coordinate

def rotate_atom_grid_xy(atoms, angle, real_unit_cell_basis=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
    """
    maps to real space using the provided unit cell basis in real space, rotates, and maps back
    """
    unit_cell_basis = numpy.matrix(real_unit_cell_basis)
    transformation_matrix = \
        numpy.linalg.inv(unit_cell_basis) * xy_rotation_matrix(angle) * unit_cell_basis
    return [Atom(atom.znucl,
                 Coordinate(transformation_matrix * col_matrix(atom.coord.coordinate_array),
                            atom.coord.coordinate_system)) \
            for atom in atoms]

def repeat_atom_grid_xy(atoms, num_times):
    """
    Returns a list of atoms repeated in the +- x and y directions num_times.
    num_times = 0 returns the original list.
    """
    return [Atom(atom.znucl, atom.coord + [a1, a2, 0])
            for a1 in xrange(-num_times, num_times+1)
            for a2 in xrange(-num_times, num_times+1)
            for atom in atoms]

def dilate_atom_grid_xy(atoms, dilation):
    """returns a list of atoms in a larger unit cell (x and y are dilated linearly)"""
    return [Atom(atom.znucl, atom.coord*[dilation, dilation, 1]) for atom in atoms]

def xy_rotation_matrix(angle):
    """returns a numpy matrix for the desired rotation around the z axis"""
    return numpy.matrix([[cos(angle), -sin(angle), 0],
                         [sin(angle), cos(angle), 0],
                         [0, 0, 1]])

def dotproduct(v1, v2):
    """Returns the dot product between two iterables"""
    return sum((a*b) for a, b in zip(v1, v2))

def length_of(v):
    """Returns the length of vector v"""
    return sqrt(dotproduct(v, v))

def angle_between(v1, v2):
    """
    returns the angle between the given vectors
    from https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    """
    return acos(dotproduct(v1, v2) / (length_of(v1) * length_of(v2)))

def col_matrix(arr):
    """returns a column vector made from the given list"""
    out = numpy.array(arr)
    out.shape = (len(arr), 1)
    return out

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


def shear_to_rhombal_grid(coordinate):
    """Maps a Coordinate from the unit grid to a 60° unit-length rhombus"""
    point = coordinate.coordinate_array
    return Coordinate(coordinate_array=[point[0]+0.5*point[1], point[1]*(3**0.5)/2, point[2]], \
                      coordinate_system=coordinate.coordinate_system)

def get_rhombal_cell(atoms):
    """given atoms in a square coordinate system, return atoms in a rhombal coordinate system."""
    return [Atom(atom.znucl, shear_to_rhombal_grid(atom.coord)) for atom in atoms]

def get_collisions(atoms, distance_threshold=0.001):
    for i in xrange(0, len(atoms)):
        for j in xrange(i + 1, len(atoms)):
            if (atoms[i].coord - atoms[j].coord).norm() < distance_threshold:
                yield (atoms[i], atoms[j])