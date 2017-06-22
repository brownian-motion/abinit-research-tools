#!/usr/bin/env python
# -*- coding=UTF-8 -*-
"""Parses an json file of band eigenenergies from Abinit, and graphs it as svg to stdout"""

__version__ = "0.0.0"

__author__ = "JJ Brown"
__copyright__ = "Copyright 2017, JJ Brown"
__credits__ = ["JJ Brown"]
__license__ = "MIT"
__maintainer__ = "JJ Brown"
__status__ = "development"

from abinit_data_types import KPointWithEnergy, KPointWithEnergyJSONDecoder
import handle_command_line_IO
import matplotlib
matplotlib.use('Agg') # Turn off display of graphs to the user; comment out this line to dispaly graphs before saving
import matplotlib.pyplot as plt # This library is very similar to MATLAB
import json
import numpy
import sys

def display_help():
    handle_command_line_IO.errprint("Usage: python graph_band_eigenvalues.py [abinit_eigenvalue_data.json [point_label_index point_label ...]]> abinit_eigenvalue_data.svg")

def create_eigenenergy_plot_figure(band_energies, energy_unit="Unknown unit", title="Band energies", special_point_labels={}):
    """Returns a plot to display the given band energies"""
    figure = plt.figure()
    axes = figure.add_subplot(111) #just one plot
    plot = axes.plot(band_energies)
    axes.set_ylabel("Band eigenenergy ("+energy_unit+")")
    axes.set_xticks([int(x) for x in special_point_labels.keys()])
    axes.set_xticklabels(special_point_labels.values())
    axes.set_title(title)
    return figure


input_file,extra_command_line_arguments = handle_command_line_IO.get_input_file(display_help)

raw_eigenvalue_data_by_k_point = sorted( \
    json.load(input_file, cls=KPointWithEnergyJSONDecoder), \
    key=lambda k: k.number \
    )

eigenenergy_data_by_point = [ k_point.band_energies for k_point in raw_eigenvalue_data_by_k_point ]
eigenenergy_data_by_band = numpy.matrix.transpose(numpy.array(eigenenergy_data_by_point))
point_labels = dict(zip(extra_command_line_arguments[::2],extra_command_line_arguments[1::2]))
plot = create_eigenenergy_plot_figure(eigenenergy_data_by_point,energy_unit=raw_eigenvalue_data_by_k_point[0].energy_unit,special_point_labels=point_labels)
plt.show(plot)
plt.savefig(sys.stdout, format="svg")