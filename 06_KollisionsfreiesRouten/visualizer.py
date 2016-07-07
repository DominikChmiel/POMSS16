#!/usr/bin/env python3
import time
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import numpy as np

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
cind = 0

T = max(endTimes) + 1
cT = 0


def plot_positions(t):
    global cind
    for x in model.getVars():
        if x.varName.startswith('x') and x.varName.endswith(str(t)) and x.x == 1:
            j = int(x.varName.split('_')[2]) - 1
            print("%d [%d:%d]" % (j, j % width, j // width), end ="\t")
            plt.plot(1 + j % width, 1 + j // width, 'o', markersize=20, color=cmap(cind))
            cind += 1
    print("")

while True:
    cind = 0
    plt.xlabel("x-Coordinate")
    plt.ylabel("y-Coordinate")
    plt.title('Timestep: ' + str(cT + 1))

    ax = plt.gca()

    ax.set_ylim(0, width + 1)
    ax.set_xlim(0, height + 1)
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
    plot_positions(cT + 1)
    plt.show(block=False)
    plt.waitforbuttonpress(timeout=1)
    plt.close()
    plt.clf()
    cT = (cT + 1) % T
