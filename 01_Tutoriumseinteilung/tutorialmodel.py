#!/usr/bin/env python3

from gurobipy import *
import itertools

def solve(nStudents, nTutorials, nTeams, groups, preferences, l, u):

    model = Model("tutorials")

    # Please use and adapt (no renaming!) the following variables:
    x = {}
    for s in range(nStudents):
        for t in range(nTutorials):
            # should have value 1 if student s is assigned to tutorial t and value 0 otherwise
            x[s,t] = model.addVar(  name="x_"+str(s)+"_"+str(t), vtype= "b", obj=preferences[s][t])
    y={}
    for t in range(nTutorials):
        # should have value 1 if tutorial t takes place and value 0 otherwise
        y[t] = model.addVar(  name="y_" +str(t) , vtype = "b")

    # end of given variables; you can introduce your own variables but make sure that the above variables attain values as stated in the comments

    model.modelSense = GRB.MAXIMIZE
    model.update()

    #constraints

    # jeder student wird zugewiesen
    for s in range(nStudents):
        model.addConstr(quicksum(x[s,t] for t in range(nTutorials)) == 1, name="Student zugewiesen_" + str(s))

    # benoetigte tutorien werden geoeffnet
    for s in range(nStudents):
        for t in range(nTutorials):
            model.addConstr(x[s,t] <= y[t], name="Student_" + str(s) + "besucht_Tutorium_" + str(t))

    # tutorium mingroesse
    for t in range(nTutorials):
        model.addConstr(quicksum(x[s,t] for s in range(nStudents)) >= l[t]*y[t], name= "mingroesse_Tutorium_" + str(t))

    # tutorium maxgroesse
    for t in range(nTutorials):
        model.addConstr(quicksum(x[s,t] for s in range(nStudents)) <= u[t]*y[t], name= "maxgroesse_Tutorium_" + str(t))

    # nur tutorien mit praeferenz groesser null
    for s in range(nStudents):
        model.addConstr(quicksum(preferences[s][t]*x[s,t] for t in range(nTutorials)) >= 1, name="valid_tutorium_fuer" + str(s))

    # teamgleichheit
    for t, team in itertools.product(range(nTutorials), range(nTeams)):
        for s1 in range(nStudents):
            if s1 in groups[team]:
                 for s2 in range(nStudents):
                      if s2 in groups[team]:
                           model.addConstr(x[s1,t] == x[s2,t])


    def printSolution():
        if model.status == GRB.status.OPTIMAL:
            for s in range(nStudents):
                for t in range(nTutorials):
                    if x[s,t].x == 1:
                        print('Student %s geht in Tutorium %s .' % (s,  t))
        else:
            print('No solution')


    #Solve
    model.optimize()
#    printSolution()

