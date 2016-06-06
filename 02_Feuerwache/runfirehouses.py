#!/usr/bin/env python3

import itertools
import os
import logging
from logging import handlers
import pprint
from gurobipy import *

# Small helpers for parsing: clean unwanted tokens / convert to float if possible
def clean_attr(attr):
    return attr.replace('#', '').strip().replace(' ', '_')

def get_value(val):
    try:
        intval = float(val)
        return intval
    except ValueError:
        return val


class FireSolver():

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

        pprint.pprint(vars(self))
        return True

    def generateInstance(self):

        model = Model('FireSolver')

        # Generate variables
        x = {}
        for bor in self.boroughs:
            # New firehouses
            for fh in self.new_firehouses + self.old_firehouses:
                val = 0
                if "currently_protected_by" in bor:
                    val = int(fh["loc_id"] == bor["currently_protected_by"])
                name = "x_" + bor["loc_id"] + "_" + fh["loc_id"]
                x[bor["loc_id"], fh["loc_id"]] = model.addVar(name=name, vtype ="b", obj=val)


        model.update()
        # Constraints: one firehouse / borough
        for bor in self.boroughs:
            model.addConstr(quicksum(x[key] for key in x if key[0] == bor["loc_id"]) == 1)

        # capacity of firehouses
        for sh in self.new_firehouses + self.old_firehouses:
            model.addConstr(quicksum(x[key] for key in x if key[1] == sh["loc_id"]) <= self.capacity)
            logging.debug('Limiting capacity of ' + sh["loc_id"])

        self.model = model

        pprint.pprint(self.model.getConstrs())

    def getInstance(self):
        return self.model


def solve(full_path_instance):
    return FireSolver(full_path_instance).getInstance()

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

solve('firedata1.csv')
