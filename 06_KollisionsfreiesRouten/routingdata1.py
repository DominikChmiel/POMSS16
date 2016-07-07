#!/usr/bin/python

from gurobipy import *

n = 2
height = 2
width = 2
startNodes = [1, 3]
targetNodes = [3, 1]
startTimes = [1, 1]
endTimes = [4, 4]

import routingmodel
model = routingmodel.solve(n, width, height, startNodes, targetNodes, startTimes, endTimes)
