#!/usr/bin/env python3
import logging
import itertools
from gurobipy import Model, GRB, quicksum

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")


def solve(n, width, height, startNodes, targetNodes, startTimes, endTimes):
    model = Model("BoatSolver")

    def toGrid(val, y=0):
        if isinstance(val, list):
            return val[0] + val[1] * width
        return val + y * width

    def fromGrid(val):
        return val % width, val // width

    # Index shift both times
    #startTimes = [x - 1 for x in startTimes]
    #endTimes = [x - 1 for x in endTimes]

    T = max(endTimes) + 1

    x = {}
    wait = {}
    for i, j, t in itertools.product(range(n), range(width * height), range(T)):
        x[i, j, t] = model.addVar(name="x_%d_%d_%d" % (i+1, j+1, t+1), vtype="b", obj=1)
    for i, j, t in itertools.product(range(n), range(width * height), range(1, T)):
        wait[i, j, t] = model.addVar(name="wait_%d_%d_%d" % (i+1, j+1, t+1), vtype="i", obj=-1)

    model.modelSense = GRB.MINIMIZE
    model.update()

    # Force startpositions
    for i, (sN, sT) in enumerate(zip(startNodes, startTimes)):
        j = toGrid(sN)
        for t in range(sT):
            logging.debug("start: %s == 1", x[i, j, t].varName)
            model.addConstr(x[i, j, t] == 1)

    # Force endpositions
    for i, (eN, eT) in enumerate(zip(targetNodes, endTimes)):
        j = toGrid(eN)
        for t in range(eT, T):
            logging.debug("end: %s == 1", x[i, j, t].varName)
            model.addConstr(x[i, j, t] == 1)

    # single container per node
    for j, t in itertools.product(range(width * height), range(T)):
        logging.debug("%s <= 1", [x[i, j, t].varName for i in range(n)])
        model.addConstr(quicksum(x[i, j, t] for i in range(n)) <= 1)

    # Force valid container movement
    for w, h in itertools.product(range(width), range(height)):
        vals = [toGrid(w, h)]
        if h >= 1:
            print("Adding " + str(w) + " : " + str(h - 1))
            vals += [toGrid(w, h - 1)]
        if w >= 1:
            print("Adding " + str(w - 1) + " : " + str(h))
            vals += [toGrid(w - 1, h)]
        if h+1 < height:
            print("Adding " + str(w) + " : " + str(h + 1))
            vals += [toGrid(w, h + 1)]
        if w+1 < width:
            print("Adding " + str(w + 1) + " : " + str(h))
            vals += [toGrid(w + 1, h)]

        print(str(w) + ":" + str(h) + " => " + str(vals))

        for i, t in itertools.product(range(n), range(1, T)):
            logging.debug("sum(%s) >= %s", [x[i, j, t].varName for j in vals], x[i, toGrid(w, h), t - 1].varName)
            model.addConstr(quicksum(x[i, j, t] for j in vals) >= x[i, toGrid(w, h), t - 1])

        for i, t in itertools.product(range(n), range(1, T)):
            logging.debug("sum(%s) <= 1", [x[i, j, t].varName for j in vals])
            model.addConstr(quicksum(x[i, j, t] for j in vals) <= 1)

    # Prevent ships from passing over same link
    for t in range(1, T):
        for w, h in itertools.product(range(width - 1), range(height)):
            for i in range(n):
                for k in range(i+1, n):
                    logging.debug("%s + %s + %s + %s <= 3", x[i, toGrid(w, h), t - 1].varName, x[i, toGrid(w + 1, h), t].varName, x[k, toGrid(w, h), t].varName, x[k, toGrid(w + 1, h), t - 1].varName)
                    model.addConstr(x[i, toGrid(w, h), t - 1] + x[i, toGrid(w + 1, h), t] + x[k, toGrid(w, h), t] + x[k, toGrid(w + 1, h), t - 1] <= 3)
        for w, h in itertools.product(range(width), range(height - 1)):
            for i in range(n):
                for k in range(i+1, n):
                    logging.debug("%s + %s + %s + %s <= 3", x[i, toGrid(w, h), t - 1].varName, x[i, toGrid(w, h + 1), t].varName, x[k, toGrid(w, h), t].varName, x[k, toGrid(w, h + 1), t - 1].varName)
                    model.addConstr(x[i, toGrid(w, h), t - 1] + x[i, toGrid(w, h + 1), t] + x[k, toGrid(w, h), t] + x[k, toGrid(w, h + 1), t - 1] <= 3)

    # Allow free waiting
    for i, j, t in itertools.product(range(n), range(width * height), range(1, T)):
        logging.debug("%s + %s - 1 <= %s", x[i, j, t - 1].varName, x[i, j, t].varName, wait[i, j, t].varName)
        model.addConstr(x[i, j, t - 1] + x[i, j, t] - 1 <= wait[i, j, t])
        logging.debug("%s >= %s", x[i, j, t].varName, wait[i, j, t].varName)
        model.addConstr(x[i, j, t - 1] >= wait[i, j, t])
        logging.debug("%s >= %s", x[i, j, t - 1].varName, wait[i, j, t].varName)
        model.addConstr(x[i, j, t] >= wait[i, j, t])


    model.optimize()

    for y in model.getVars():
        if y.varName.startswith('x') and y.x:
            logging.debug("%s = %d", y.varName, y.x)

    return model
