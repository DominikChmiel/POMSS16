#!/usr/bin/env python3
import os
import logging
from gurobipy import Model, GRB, quicksum


# Returns a valid identifier and array-size based on the given token.
# Token will be first string at the beginning of a line, and comes in 3 vars:
# 1. nProducts  => can be taken directly, dimension 0
# 2. l:         => doesn't end in number, return dimension 1, l
# 3. d1:        => ends in number, return dimensions 2, d (Assumption: Lines will be processed in order, so actual value doesn't matter)
def getIdentfier(ident):
    dims = 0
    if ident.endswith(':'):
        ident = ident[:-1]
        dims = 1
        rev = ident[::-1]
        index = -1
        # Extract number from the end of string
        while rev and rev[0].isdigit():
            index = index * 10 + int(rev[0])
            rev = rev[1::]
        if index != -1:
            dims = 2
            name = rev[::-1]
        else:
            name = ident
    else:
        name = ident
    return dims, name


class LotSolver(object):
    model = None
    store = {}

    def __init__(self, filePath):
        if self.import_txt(filePath):
            self.generateInstance()
        else:
            logging.error('Error during parsing. Instance will not be valid.')

    # Processes content of file
    def process_txt(self, content):
        if not content:
            return False

        values = ''
        lines = content.strip().split('\n')
        lines.sort()                         # Sort lines in case that the numbers aren't in sequence
        for line in lines:
            # remove duplicate strings
            line = " ".join(line.split())
            tokens = line.split(' ')
            values = [float(x) if float(x) % 1 != 0 else int(float(x)) for x in tokens[1::]]
            if not values:
                continue
            dims, name = getIdentfier(tokens[0])
            if dims == 0:
                if len(values) != 1:
                    logging.error('Invalid input for token: ' + tokens[0])
                    return False
                logging.debug(name + " => " + str(values[0]))
                self.store[name] = values[0]
            elif dims == 1:
                logging.debug(name + " => " + str(values))
                self.store[name] = values
            else:
                if name not in self.store:
                    logging.debug("Initializing " + name)
                    self.store[name] = []
                # Assumption made here: e.g. lines d1 d2 and d3 appear in sequence in lines-list
                self.store[name].append(values)
                logging.debug('New value for ' + name + ': ' + str(self.store[name]))

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
        if not all([x in self.store for x in ["Timehorizon", "h", "K", "a", "d", "s", "st"]]):
            logging.error('Store is not initialized correctly. Check for completeness of input-file.')
            return None

        model = Model("LotSolver")

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
    return LotSolver(full_path_instance).getInstance()
