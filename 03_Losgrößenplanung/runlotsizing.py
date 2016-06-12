# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import os
import logging
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

class LotSolver(object):
    
    model = None
    
    def __init__(self, filePath):
        if self.import_txt(filePath):
            self.generateInstance()
        else:
            logging.error('Error during parsing. Instance will not be valid.')
    
    #process one line of the file        
    def process_line(self, line):
        if not line:
            return False
        
        identifier = ''
        values = ''
        if ':' in line:
            identifier, valueLine = line.split(':')
            values = valueLine.split()
            valList = []
            # save i as key, corresponding value as value for each variable
            # e.g. l : (0, value), (1, value)...
            for i in range(0, len(values)):
                newVal = {}
                key = str(i)
                newVal[clean_attr(key)] = get_value(values[i])
                valList.append(newVal)
            self.__setattr__(clean_attr(identifier), valList)
        else:
            # either nProducts or TimeHorizon, save directly as variable
            identifier, value = line.split()
            self.__setattr__(clean_attr(identifier), get_value(value.strip()))
        return True

        
    def import_txt(self, filePath):
        if not os.path.exists(filePath):
            logging.error("Invalid file-path.")
            return False
        if not filePath.endswith('.txt'):
            logging.error("Not a valid input file.")
            return False
        with open(filePath) as f:
            content = f.read()
            lines = content.strip().split('\n')
            for l in lines:
                self.process_line(l)
        return True

    def generateInstance(self):
        
        model = Model("LotSolver")
        
        #TODO Model
        
        # solve it
        model.optimize()

        self.model = model
    
    def getInstance(self):
        return self.model

def solve(full_path_instance):
    return LotSolver(full_path_instance).getInstance()