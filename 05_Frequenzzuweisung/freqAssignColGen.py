from gurobipy import *
import math

def solve(positions, radius):

    print("%d Antennen, Radius = %g" % (len(positions), radius))

    # calculate euclidean distance
    def euc_dist(pos1, pos2):
        dx = positions[pos1][0] - positions[pos2][0]
        dy = positions[pos1][1] - positions[pos2][1]
        return math.sqrt(dx * dx + dy * dy)

    numAntennas = len(positions)

    rmp = Model("Frequency assignment RMP")

    # variables
    # distribution[] has number of antennas as colums and their corresponding frequency as row value
    distribution = []
    y = []
    distribution.append([0])
    for a in range(numAntennas):
        #every antenna gets own frequence as starting point
        distribution[0].append(a)
        #print(distribution)
        y.append(rmp.addVar(lb=0., ub=GRB.INFINITY, name = "frequenz_" + str(a), obj=1.0))

    # minimize
    rmp.modelSense = GRB.MINIMIZE
    # update model
    rmp.update()

    # critical radius constraint
    cons = []
    for a1 in xrange(numAntennas):
        for a2 in xrange(numAntennas):
            # radius check
            if (euc_dist(positions[a1], positions[a2]) <= radius):
                for i in xrange(distribution):
                    cons.append( rmp.addConstr(distribution[i][a1] != distribution[i][a2]))


    solveIP = False
    while True:
        rmp.update()
        rmp.optimize()

        if solveIP:
            break

        pp = Model("Frequency assignment PP")
        pp.setAttr("objCon", 1.)

        # dual variables for pp
        x = {}
        for i in xrange(numAntennas):
            x[i] = pp.addVar(lb=0., ub=GRB.INFINITY, name="x_" + str(i), obj=-1.0 * cons[i].pi,
                                    vtype=GRB.INTEGER)
        pp.modelSense = GRB.MINIMIZE
        pp.update()

        #pricing model constraints
        #TODO

        pp.optimize()

        #if pp.objval < -0.001:
             #TODO
        #else:
         #   for i in xrange(len(y)):
          #      y[i].vtype = GRB.INTEGER
           # solveIP = True
    # Essenzielle Bedingung: Das RMP- und PP-Modellobjekt muessen zurueckgegeben werden!
    return (rmp, pp)
