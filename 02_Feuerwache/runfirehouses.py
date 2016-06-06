#!/usr/bin/env python3
import os
import logging
import math
from gurobipy import Model, GRB, quicksum


# Small helpers for parsing: clean unwanted tokens / convert to float if possible
def clean_attr(attr):
    return attr.replace('#', '').strip().replace(' ', '_')


def get_value(val):
    try:
        intval = float(val)
        return intval
    except ValueError:
        return val


class FireSolver(object):

    model = None

    def __init__(self, filePath):
        if self.import_csv(filePath):
            self.generateInstance()
        else:
            logging.error('Error during parsing. Instance will not be valid.')


    # Processes a single block form the input-file. Blocks are designated + split by the \n# marker (assumption for simplicity).
    def process_block(self, block):
        if not block:
            return False
        lines = block.strip().split('\n') # Remove whitespace + split into lines

        if len(lines) < 2:
            logging.warning('Malformed block: ' + block)
            return False

        # Line 0 contains identifiers, parse those
        identifier = ''
        members = ''
        if ':' in lines[0]:
            identifier, memberLine = lines[0].split(':')
            members = memberLine.split(',')
            valList = []
            for line in lines[1::]:
                newVal = {}
                for key, value in zip(members, line.split(',')):
                    newVal[clean_attr(key)] = get_value(value.strip())
                valList.append(newVal)
            self.__setattr__(clean_attr(identifier), valList)
        else:
            members = lines[0].split(',')
            values = lines[1].split(',')
            for key, value in zip(members, values):
                self.__setattr__(clean_attr(key), get_value(value.strip()))
        return True

    def import_csv(self, filePath):
        if not os.path.exists(filePath):
            logging.error("Invalid file-path.")
            return False
        if not filePath.endswith('.csv'):
            logging.error("Not a valid input file.")
            return False
        with open(filePath) as f:
            content = f.read()
            blocks = content.split('\n#')
            for x in blocks:
                self.process_block(x)
        return True

    def generateInstance(self):

        def euc_dist(bor, sh):
            dx = bor["x_coord"] - sh["x_coord"]
            dy = bor["y_coord"] - sh["y_coord"]
            return math.sqrt(dx * dx + dy * dy)

        model = Model('FireSolver')

        # Generate variables
        x = {}
        for bor in self.boroughs:
            # New firehouses
            for fh in self.new_firehouses + self.old_firehouses:
                name = "x_" + fh["loc_id"] + "_" + bor["loc_id"]
                print(name)
                x[bor["loc_id"], fh["loc_id"]] = model.addVar(name=name, vtype ="b", obj=self.cost_coef * euc_dist(bor, fh))

        # Open variables
        openfh = {}
        for fh in self.new_firehouses:
            openfh[fh["loc_id"]] = model.addVar(name = "open_" + fh["loc_id"], vtype ="b", obj=fh["construction_cost"])

        # Close variables
        closefh = {}
        for fh in self.old_firehouses:
            closefh[fh["loc_id"]] = model.addVar(name = "close_" + fh["loc_id"], vtype ="b", obj=fh["destruction_cost"])

        model.modelSense = GRB.MINIMIZE
        model.update()

        # Constraints: one firehouse / borough
        for bor in self.boroughs:
            model.addConstr(quicksum(x[key] for key in x if key[0] == bor["loc_id"]) == 1)

        # capacity of firehouses
        for fh in self.new_firehouses:
            model.addConstr(quicksum(x[key] for key in x if key[1] == fh["loc_id"]) <= self.capacity * openfh[fh["loc_id"]])

        # If it is not removed, the initial assignment needs to be respected
        for fh in self.old_firehouses:
            for bor in self.boroughs:
                if bor["currently_protected_by"] == fh["loc_id"]:
                    model.addConstr(x[bor["loc_id"], fh["loc_id"]] == 1 - closefh[fh["loc_id"]])
        
        # solve it
        model.optimize()

        self.model = model

    def getInstance(self):
        return self.model


def solve(full_path_instance):
    return FireSolver(full_path_instance).getInstance()