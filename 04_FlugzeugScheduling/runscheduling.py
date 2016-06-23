#!/usr/bin/env python3
import os
import logging
from gurobipy import Model, GRB, quicksum


class PlaneSolver(object):
    model = None

    n = 0
    T = 0
    planes = []

    def __init__(self, filePath):
        if self.import_txt(filePath):
            self.generateInstance()
        else:
            logging.error('Error during parsing. Instance will not be valid.')

    # Processes content of file
    def process_txt(self, content):
        if not content:
            return False

        values = []
        # Remove duplicate spaces + remove newlines
        content = " ".join(content.replace('\n', ' ').split())
        try:
            values = [float(x) if float(x) % 1 != 0 else int(float(x)) for x in content.split()]
        except ValueError as e:
            logging.error('Invalid token in input-file.')
            logging.error(e)
            return False
        if len(values) <= 2:
            logging.error('Too few values in input file.')
            return False
        self.n = values[0]
        self.T = values[1]
        values = values[2::]
        if len(values) < self.n * (6 + self.n):
            logging.error('Too few values in plane-data.')
            return False
        if len(values) > self.n * (6 + self.n):
            logging.warning('Additional tokens at end of input file.')
        for _ in range(self.n):
            plane = {}
            for k, v in zip(["a", "r", "b", "d", "g", "h"], values[0:6]):
                plane[k] = v
            plane["s"] = values[6:6 + self.n]
            values = values[6 + self.n::]

            self.planes.append(plane)

        return True

    # Tries to locate file given by <filePath> and passes it to process_txt
    def import_txt(self, filePath):
        if not os.path.exists(filePath):
            logging.error("Invalid file-path.")
            return False
        if not filePath.endswith('.txt'):
            logging.error("Not a valid input file.")
            return False
        self.planes = []
        self.n = 0
        self.T = 0
        with open(filePath) as f:
            content = f.read()
            return self.process_txt(content)

    def generateInstance(self):
        # Check that variables have been intialized correctly
        if (not self.planes) or (self.n == 0) or (self.T == 0):
            logging.error('Store is not initialized correctly. Check for completeness of input-file.')
            return None

        model = Model("PlaneSolver")

        """
            r: Earliest landing possibility
            b: Best landing
            d: latest landing
            g: penalty for each time earlier from best
            h: penalty for each time later from best
            s_ij: if i lands before j: s needs to pass in time

            x_i: Landing time for i
            p_i: positive divertion from bi
            n_i: negative divertion from bi

        """

        bigM = max([max(x["s"]) for x in self.planes])
        logging.debug("Using bigM punishment: " + str(bigM))

        # generate Variables
        x = {}  # Landing time
        p = {}  # Positive divertion from optimal landing time
        n = {}  # Negative divertion from optimal landing time
        s = {}  # 1 iff plane i lands before j + buffer is invalid
        s1 = {}  # for these, see constraints
        s2 = {}
        h1 = {}
        h2 = {}
        for i in range(len(self.planes)):
            x[i] = model.addVar(name="x_%d" % (i+1), vtype="i", lb=self.planes[i]["r"], ub=self.planes[i]["d"])
            p[i] = model.addVar(name="p_%d" % (i+1), vtype="i", obj=self.planes[i]["h"], lb=0, ub=self.planes[i]["d"] - self.planes[i]["b"])
            n[i] = model.addVar(name="n_%d" % (i+1), vtype="i", obj=self.planes[i]["g"], lb=0, ub=self.planes[i]["b"] - self.planes[i]["r"])

            for j in range(len(self.planes)):
                s[i, j] = model.addVar(name="s_%d_%d" % (i+1, j+1), vtype="b", obj=bigM, lb=0, ub=1)
                s1[i, j] = model.addVar(name="s1_%d_%d" % (i+1, j+1), vtype="b", obj=0, lb=0, ub=1)
                s2[i, j] = model.addVar(name="s2_%d_%d" % (i+1, j+1), vtype="b", obj=0, lb=0, ub=1)
                h1[i, j] = model.addVar(name="h1_%d_%d" % (i+1, j+1), vtype="i", obj=0, lb=0)
                h2[i, j] = model.addVar(name="h2_%d_%d" % (i+1, j+1), vtype="i", obj=0, lb=0)

        model.modelSense = GRB.MINIMIZE
        model.update()

        for y in model.getVars():
            if y.ub < 10000:
                logging.debug("%10s\t[%5d:%5d]\tobj %4d", y.varName, y.lb, y.ub, y.obj)

        # Constraints
        for i in range(len(self.planes)):
            logging.debug("{} == {} + {} - {}".format(x[i].varName, self.planes[i]["b"], p[i].varName, n[i].varName))
            model.addConstr(x[i] == self.planes[i]["b"] + p[i] - n[i])

            for j in range(len(self.planes)):
                if j == i:
                    continue
                # model.addConstr(x[j] - x[i] )
                # Force s = s1 AND s2
                model.addConstr(s[i, j] <= s1[i, j])
                model.addConstr(s[i, j] <= s2[i, j])
                model.addConstr(s[i, j] >= s1[i, j] + s2[i, j] - 1)

                # s2 == xj - xi > 0
                logging.debug("{}\t <= {}\t - {}\t - {}\t".format(s2[i, j].varName, x[j].varName, x[i].varName, h1[i, j].varName))
                model.addConstr(s2[i, j] <= x[j] - x[i] + h1[i, j])
                logging.debug("{}\t >= 1\t".format(h1[i, j].varName))
                model.addConstr(h1[i, j] >= 1)
                logging.debug("{}\t - {}\t + {}\t <= {}\t*{}\t".format(x[j].varName, x[i].varName, h1[i, j].varName, s2[i, j].varName, bigM))
                model.addConstr(x[j] - x[i] + h1[i, j] <= s2[i, j]*bigM)

                # s1 == xi + sij - xj > 0
                logging.debug("{}\t + {}\t - {}\t >= {}\t".format(x[i].varName, self.planes[i]["s"][j], x[j].varName, s1[i, j].varName))
                model.addConstr(s1[i, j] <= x[i] + self.planes[i]["s"][j] - x[j] + h2[i, j])
                logging.debug("{}\t + {}\t - {}\t <= {}\t*{}\t".format(x[i].varName, self.planes[i]["s"][j], x[j].varName, s1[i, j].varName, bigM))
                model.addConstr(x[i] + self.planes[i]["s"][j] - x[j] <= s1[i, j]*bigM)

        # solve it
        model.optimize()

        # Debugging printouts
        dbgStrs = {}
        for y in model.getVars():
            if y.varName[0:2] not in dbgStrs:
                dbgStrs[y.varName[0:2]] = []
            dbgStrs[y.varName[0:2]].append("%8s = %4s [%4s]" % (y.varName, int(y.x), int(y.x*y.obj) if y.obj else ""))
        for x in dbgStrs:
            dbgStrs[x].sort()

        while dbgStrs:
            printed = False
            keys = [x for x in dbgStrs.keys()]
            keys.sort()
            logStr = ""
            for x in keys:
                if dbgStrs[x]:
                    logStr += dbgStrs[x][0]
                    dbgStrs[x] = dbgStrs[x][1::]
                    printed = True
                else:
                    logStr += " "*22
            logging.debug(logStr)
            if not printed:
                break

        self.model = model

    def getInstance(self):
        return self.model


def solve(full_path_instance):
    return PlaneSolver(full_path_instance).getInstance()
