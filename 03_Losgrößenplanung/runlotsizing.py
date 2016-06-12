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
        self.l = []
        self.d = []
        self.s = []
        self.st = []
        if self.import_txt(filePath):
            #print(vars(self))
            self.generateInstance()
        else:
            logging.error('Error during parsing. Instance will not be valid.')
    
    #process one line of the file        
    def process_txt(self, content):
        if not file:
            return False
        
        identifier = ''
        values = ''
        lines = content.strip().split('\n')
        for line in lines:
            if ':' in line:
                identifier, valueLine = line.split(':')
                values = valueLine.split()
                valList = []
                print("\ninput_line_identifier: " + identifier)
                print(values)
                if len(identifier) == 1:
                    # create 2d array with products as columns and stock at t as rows 
                    if identifier == 'l':
                        for i in range(len(values)):
                            l0 = []
                            l0.append(values[i])
                            print(l0)
                            self.l.append(l0)
                            
                        print(self.l)
                    # save i as key, corresponding value as value for each variable for h, K, a
                    else:
                        for i in range(len(values)):
                            valList.append(int(values[i]))
                            print(valList)
                        self.__setattr__(clean_attr(identifier), valList)
                # create 2d array for d and s of the form [product][valuelist for each product]
                if len(identifier) == 2:
                    iType, number = identifier[:1], identifier[-1:]
                    index = int(number)
                    print(index)
                    if iType == 'd':
                        self.d.insert(index-1, values)
                        print(self.d)
                    elif iType == 's':
                        self.s.insert(index-1, values)
                        print(self.s)
                # create 2d array for st of the form [product][valuelist for each product]
                if len(identifier) == 3:
                    iType, number = identifier[:2], identifier[-1:]
                    index = int(number)
                    self.st.insert(index-1, values)
                    print(self.st)
            else:
                # either nProducts or TimeHorizon, save directly as variable
                identifier, value = line.split()
                print(identifier + " " + value)
                self.__setattr__(clean_attr(identifier), int(value.strip()))
            
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
            self.process_txt(content)
        return True

    def generateInstance(self):
        
        model = Model("LotSolver")
        
        # generate Variables
        x = {}
        for p in range(1, self.nProducts+1):
            for t in range(1, self.Timehorizon+1):
                name = "x_" + str(p) + "_" + str(t)
                print(name)
                # obj=?
                x[p, t] = model.addVar(name = name, vtype = "i")
        
        # switch costs
        s = {}
        for p1 in range(self.nProducts):
            for p2 in range(self.nProducts):
                name = "s_" + str(p1) + "_" + str(p2)
                s[p1, p2] = model.addVar(name = name, vtype = "i", obj = float(self.s[p1][p2]))
        
        # switch time
        st = {}
        for p1 in range(self.nProducts):
            for p2 in range(self.nProducts):
                name = "st_" + str(p1) + "_" + str(p2)
                st[p1, p2] = model.addVar(name = name, vtype = "i", obj = float(self.st[p1][p2]))        
        
        
        model.modelSense = GRB.MINIMIZE
        model.update()
        
        # Constraints
                
        
        # solve it
        model.optimize()

        self.model = model
    
    def getInstance(self):
        return self.model

def solve(full_path_instance):
    return LotSolver(full_path_instance).getInstance()