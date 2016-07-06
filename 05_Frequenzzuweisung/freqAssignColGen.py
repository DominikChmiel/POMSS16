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
    print("Berechnung laeuft...")
    rmp.params.outputFlag = 0

    # variables
    # distribution[f][a]: frequency f used by antenna a
    # y[f]: 1 if frequency f is used
    distribution = []
    y = []
    for a in range(numAntennas):
        distribution.append([0]*numAntennas)
        # every antenna has own frequency at start (worst case)
        distribution[a][a] = 1
        y.append(rmp.addVar(lb=0., ub=1, name="frequenz_" + str(a), obj=1.0))

    # minimize
    rmp.modelSense = GRB.MINIMIZE
    # update model
    rmp.update()

    # rmp constraint
    cons = []
    # every antenna gets one frequency
    for a in range(numAntennas):
        cons.append(rmp.addConstr(quicksum(distribution[f][a]*y[f] for f in range(numAntennas)) >= 1))

    #rmp.write("rmp.lp")
    #rmp.write("rmp.mps")

    solveIP = False
    while True:
        rmp.update()
        rmp.optimize()

        if solveIP:
            break

        pp = Model("Frequency assignment PP")
        pp.params.outputFlag = 0
        pp.setAttr("objCon", 1.)

        # dual variables for pp
        x = {}
        for i in range(numAntennas):
            x[i] = pp.addVar(lb=0., ub=1, name="x_" + str(i), obj=-1.0*cons[i].pi, vtype="b")

        # minimize
        pp.modelSense = GRB.MINIMIZE
        # update pricing model
        pp.update()

        # pricing model constraint
        for a1 in range(numAntennas):
            for a2 in range(numAntennas):
                # radius check
                if a1 != a2 and euc_dist(a1, a2) <= radius:
                    pp.addConstr(x[a1] + x[a2] <= 1)

        pp.optimize()
        if pp.status != GRB.status.OPTIMAL:
            raise Exception("Pricing-Problem konnte nicht geloest werden!")

        if pp.objval < -0.001:
            new = [int(x[i].x + 0.5) for i in range(numAntennas)]
            distribution.append(new)
            y.append(rmp.addVar(lb=0., ub=1, name="verteilung_"+str(len(y)), obj=1.0, column=Column(new, cons)))
        else:
            # not converting to integer here because it was not requested
            # for i in range(len(y)):
            #     y[i].vtype = GRB.INTEGER
            solveIP = True
    print('Zielfunktionswert: %f' % (rmp.getObjective().getValue()))
    # Essenzielle Bedingung: Das RMP- und PP-Modellobjekt muessen zurueckgegeben werden!
    return (rmp, pp)
