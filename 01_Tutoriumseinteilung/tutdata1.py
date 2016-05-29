#!/usr/bin/python


from gurobipy import *


nStudents=10

nTutorials=2

nTeams=3

groups=[  [1,2,0],
          [4,5,3],
          [7,8,6] ]

preferences =[ [0, 50],
              [100 , 25],
              [100 , 25],
              [100, 25], 
              [100, 25],
              [25, 100],
              [100, 25],
              [100 , 25], 
              [25 ,100],
              [100  ,50]  ]

l = [1, 4]
u = [6, 6]

import tutorialmodel
tutorialmodel.solve(nStudents, nTutorials, nTeams, groups, preferences, l, u)
