#!/usr/bin/env python3
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook


from runfirehouses import FireSolver

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

solver = FireSolver('firedata1.csv')

marker_style = dict(linestyle=':', color='cornflowerblue', markersize=10)


#ax.scatter(delta1[:-1], delta1[1:], c=close, s=volume, alpha=0.5)
plt.figure(1)
plt.xlabel("x-Coordinate")
plt.ylabel("y-Coordinate")
plt.title('Solution of Group')

def renderSet(inputData, style):
    x_data =  []
    y_data = []
    for inp in inputData:
        x_data.append(inp["x_coord"])
        y_data.append(inp["y_coord"])
    plt.plot(x_data, y_data, style)

def renderLine(bid, fid, style):
    x_data = []
    y_data = []
    for x in solver.boroughs:
        if x["loc_id"] == bid:
            x_data.append(x["x_coord"])
            y_data.append(x["y_coord"])
    for x in solver.new_firehouses + solver.old_firehouses:
        if x["loc_id"] == fid:
            x_data.append(x["x_coord"])
            y_data.append(x["y_coord"])
    plt.plot(x_data, y_data, style)

# Render utilized connections

for x in solver.model.getVars():
    if x.x == 1:
        if x.varName.startswith('x'):
            bid, fid = x.varName.split('_')[1::]
            renderLine(bid, fid, 'k-')

# Plot all locations
renderSet(solver.new_firehouses, 'bo')
renderSet(solver.old_firehouses, 'yo')
renderSet(solver.boroughs, 'ks')

plt.grid(True)

plt.show()