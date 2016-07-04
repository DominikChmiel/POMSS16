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
    # distribution[f][a]: frequency f used by antenna a
    # y[f]: number of uses of frequency f
    distribution = []
    y = []
    for a in range(numAntennas):
        distribution.append([0]*numAntennas)
        distribution[a][a] = 1
        y.append(rmp.addVar(lb=0., ub=GRB.INFINITY, name="frequenz_" + str(a), obj=1.0))

    # minimize
    rmp.modelSense = GRB.MINIMIZE
    # update model
    rmp.update()

    # critical radius constraint
    cons = []
    # every antenna gets exactly one frequency and the frequency must be activated
    for a in xrange(numAntennas):
        cons.append(rmp.addConstr(quicksum(distribution[f][a] for f in xrange(len(distribution))) == 1 and y[a] >= 1))


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
            x[i] = pp.addVar(lb=0., ub=GRB.INFINITY, name="x_" + str(i), obj=-1.0 * cons[i].pi, vtype=GRB.INTEGER)
        pp.modelSense = GRB.MINIMIZE
        pp.update()

        #pricing model constraints
        #???
        for a1 in xrange(numAntennas):
            for a2 in xrange(numAntennas):
                # radius check
                if (euc_dist(a1, a2) <= radius):
                    cons.append(rmp.addConstr(distribution[f][a1] != distribution[f][a2] for f in xrange(len(distribution))))

        pp.optimize()

        if pp.objval < -0.001:
            #???
             new = [int(x[i].x) for i in xrange(numAntennas)]
             distribution.append(new)
             y.append(rmp.addVar(lb=0., ub=GRB.INFINITY, name="verteilung_"+str(len(y)), obj=1.0, column=Column(new, cons)))
        else:
           for i in xrange(len(y)):
               y[i].vtype = GRB.INTEGER
           solveIP = True
    # Essenzielle Bedingung: Das RMP- und PP-Modellobjekt muessen zurueckgegeben werden!
    return (rmp, pp)
