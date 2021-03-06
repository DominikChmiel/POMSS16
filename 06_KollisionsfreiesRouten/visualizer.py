#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import numpy as np
import sys

from routingdata2 import *


def get_cmap(N):
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
    RGB color.'''
    color_norm = colors.Normalize(vmin=0, vmax=N-1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')

    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color
cmap = get_cmap(n + 2)

T = max(endTimes) + 1
cT = 0

def plot_positions(t):
    for x in model.getVars():
        if x.varName.startswith('x') and x.varName.endswith(str(t)) and x.x == 1:
            parts = x.varName.split('_')
            j = int(parts[2]) - 1
            plt.plot(1 + j % width, height - (j // width), 'o', markersize=20, color=cmap(int(parts[1]) - 1))

for i in range(1, T):
    plt.figure(i)
    plt.xlabel("x-Coordinate")
    plt.ylabel("y-Coordinate")
    plt.title('Timestep: ' + str(i))

    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
    #           ncol=2, mode="expand", borderaxespad=0.)
    handles = []
    for x in range(n):
        handles.append(mpatches.Patch(color=cmap(x), label='S' + str(x+1)))
    plt.legend(handles=handles)

    ax = plt.gca()

    ax.set_xlim(0, width + 1)
    ax.set_ylim(0, height + 1)
    major_ticks = np.arange(0 + 1, max(width, height) + 1, 1)
    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)

    ax.grid(True)

    ticklines = ax.get_xticklines() + ax.get_yticklines()
    gridlines = ax.get_xgridlines() + ax.get_ygridlines()
    ticklabels = ax.get_xticklabels() + ax.get_yticklabels()

    for line in ticklines:
        line.set_linewidth(3)

    for line in gridlines:
        line.set_linestyle('-')

    plot_positions(i)

    moduleID = '1'
    for x in sys.modules.keys():
        if x.startswith('routingdata'):
            moduleID = x[-1]

    plt.savefig('data_' + str(moduleID) + '/routing_t_' + str(i))

plt.show()
    #plt.waitforbuttonpress(timeout=1)
    #
    #plt.close()
    #plt.clf()
    #cT = (cT + 1) % T
