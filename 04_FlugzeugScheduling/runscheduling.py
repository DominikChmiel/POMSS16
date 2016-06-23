#!/usr/bin/env python3
import os
import logging
from gurobipy import Model, GRB, quicksum
import pprint



class PlaneSolver(object):
    model = None
    store = {}

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
        pprint.pprint(self.planes)

        return True

    # Tries to locate file given by <filePath> and passes it to process_txt
    def import_txt(self, filePath):
        if not os.path.exists(filePath):
            logging.error("Invalid file-path.")
            return False
        if not filePath.endswith('.txt'):
            logging.error("Not a valid input file.")
            return False
        self.store = {}
        with open(filePath) as f:
            content = f.read()
            return self.process_txt(content)

    def generateInstance(self):
        # Check that store has been intialized correctly
        if (not self.planes) or (self.n == 0) or (self.T == 0):
            logging.error('Store is not initialized correctly. Check for completeness of input-file.')
            return None

        model = Model("PlaneSolver")

        # generate Variables

        model.modelSense = GRB.MINIMIZE
        model.update()

        for y in model.getVars():
            logging.debug("%s obj %s", y.varName, y.obj)

        # Constraints

        # solve it
        model.optimize()

        # Debugging printouts
        for y in model.getVars():
            if y.x >= 0.001:
                logging.debug("%s = %s cost %d", y.varName, y.x, y.x*y.obj)

        self.model = model

    def getInstance(self):
        return self.model


def solve(full_path_instance):
    return PlaneSolver(full_path_instance).getInstance()
