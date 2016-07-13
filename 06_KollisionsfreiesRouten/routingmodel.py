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

    T = max(endTimes)

    x = {}
    wait = {}
    for i, j, t in itertools.product(range(n), range(width * height), range(T)):
        x[i, j, t] = model.addVar(name="x_%d_%d_%d" % (i+1, j+1, t+1), vtype="b", obj=1)
        wait[i, j, t] = model.addVar(name="wait_%d_%d_%d" % (i+1, j+1, t+1), vtype="i", obj=-1)

    model.modelSense = GRB.MINIMIZE
    model.update()

    # Force startpositions
    for i, (sN, sT) in enumerate(zip(startNodes, startTimes)):
        for t in range(sT):
            for j in range(width * height):
                if j == toGrid(sN - 1) and t == sT - 1:
                    logging.debug("start: %s == 1", x[i, j, t].varName)
                    model.addConstr(x[i, j, t] == 1)
                else:
                    logging.debug("start: %s == 0", x[i, j, t].varName)
                    model.addConstr(x[i, j, t] == 0)

    # Force endpositions
    for i, (eN, eT) in enumerate(zip(targetNodes, endTimes)):
        j = toGrid(eN - 1)
        logging.debug("end: %s == 1", x[i, j, eT - 1].varName)
        model.addConstr(x[i, j, eT - 1] == 1)
        # Container vanishes after endTime
        for t in range(eT, T):
            logging.debug("end: %s == 0", x[i, j, t].varName)
            model.addConstr(x[i, j, t] == 0)

    # single container per node
    for j, t in itertools.product(range(width * height), range(T)):
        logging.debug("%s <= 1", [x[i, j, t].varName for i in range(n)])
        model.addConstr(quicksum(x[i, j, t] for i in range(n)) <= 1)

    # Force valid container movement
    for w, h in itertools.product(range(width), range(height)):
        vals = [toGrid(w, h)]
        if h >= 1:
            vals += [toGrid(w, h - 1)]
        if w >= 1:
            vals += [toGrid(w - 1, h)]
        if h+1 < height:
            vals += [toGrid(w, h + 1)]
        if w+1 < width:
            vals += [toGrid(w + 1, h)]

        for i, t in itertools.product(range(n), range(1, T)):
            if endTimes[i] > t and startTimes[i] <= t:
                logging.debug("sum(%s) >= %s", [x[i, j, t].varName for j in vals], x[i, toGrid(w, h), t - 1].varName)
                model.addConstr(quicksum(x[i, j, t] for j in vals) >= x[i, toGrid(w, h), t - 1])
            else:
                logging.debug("skipped(%s) >= %s", [x[i, j, t].varName for j in vals], x[i, toGrid(w, h), t - 1].varName)

        for i, t in itertools.product(range(n), range(1, T)):
            logging.debug("sum(%s) <= 1", [x[i, j, t].varName for j in vals])
            model.addConstr(quicksum(x[i, j, t] for j in vals) <= 1)

    # Force continous line through grid
    for i, t in itertools.product(range(n), range(0, T)):
        if endTimes[i] > t and startTimes[i] <= t + 1:
            logging.debug("sum(%s) == 1", [x[i, j, t].varName for j in range(width * height)])
            model.addConstr(quicksum(x[i, j, t] for j in range(width * height)) == 1)
        else:
            logging.debug("sum(%s) == 0", [x[i, j, t].varName for j in range(width * height)])
            model.addConstr(quicksum(x[i, j, t] for j in range(width * height)) == 0)

    # Prevent ships from passing over same link
    for t in range(1, T):
        for w, h in itertools.product(range(width - 1), range(height)):
            for i in range(n):
                for k in range(i+1, n):
                    model.addConstr(x[i, toGrid(w, h), t - 1] + x[i, toGrid(w + 1, h), t] + x[k, toGrid(w, h), t] + x[k, toGrid(w + 1, h), t - 1] <= 3)
                    model.addConstr(x[i, toGrid(w, h), t] + x[i, toGrid(w + 1, h), t - 1] + x[k, toGrid(w, h), t - 1] + x[k, toGrid(w + 1, h), t] <= 3)
        for w, h in itertools.product(range(width), range(height - 1)):
            for i in range(n):
                for k in range(i+1, n):
                    model.addConstr(x[i, toGrid(w, h), t - 1] + x[i, toGrid(w, h + 1), t] + x[k, toGrid(w, h), t] + x[k, toGrid(w, h + 1), t - 1] <= 3)
                    model.addConstr(x[i, toGrid(w, h), t] + x[i, toGrid(w, h + 1), t - 1] + x[k, toGrid(w, h), t - 1] + x[k, toGrid(w, h + 1), t] <= 3)

    # Allow free waiting
    for i, j, t in itertools.product(range(n), range(width * height), range(1, T)):
        model.addConstr(x[i, j, t - 1] + x[i, j, t] - 1 <= wait[i, j, t])
        model.addConstr(x[i, j, t - 1] >= wait[i, j, t])
        model.addConstr(x[i, j, t] >= wait[i, j, t])

    # Initial state: Waiting is free
    for i, j in itertools.product(range(n), range(width * height)):
        model.addConstr(x[i, j, 0] == wait[i, j, 0])

    model.optimize()

    for y in model.getVars():
        if y.x:
            logging.warning("%s = %d", y.varName, y.x)

    return model
