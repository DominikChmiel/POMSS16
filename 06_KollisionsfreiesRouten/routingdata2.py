#!/usr/bin/python

from gurobipy import *

n = 4
height = 3
width = 4
startNodes = [1, 12, 3, 9]
targetNodes = [11, 1, 12, 3]
startTimes = [1, 1, 2, 2]
endTimes = [6, 6, 6, 6]

import routingmodel
model = routingmodel.solve(n, width, height, startNodes, targetNodes, startTimes, endTimes)
