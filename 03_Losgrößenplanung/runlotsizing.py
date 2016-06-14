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
        with open(filePath) as f:
            content = f.read()
            return self.process_txt(content)

    def generateInstance(self):
        # Check that store has been intialized correctly
        if not all([x in self.store for x in ["Timehorizon", "h", "K", "a", "d", "s", "st"]]):
            logging.error('Store is not initialized correctly. Check for completeness of input-file.')
            return None

        model = Model("LotSolver")

        """
            Problem:
                Timehorizon: Number of periods
                l: Anfangslagerbestand
                ab t=1:
                    In jeder periode Muss bedarf von Kunden gedeckt werden (d[i])
                    Ueberschuessiges in lager, kosten von h[i] / time
                    Pro periode K[i] stunden / maschine
                    Pro produkt [i] a[i] stunden
                    1x umruesten / maschine / periode, kosten s[i][j], st[i][j] std (von prod i => j)

            variables:
                x_[prod]_[period]: produziert / periode
                l_[prod]_[period]: lager von periode => periode + 1
                switch_[p1]_[p2]_[period]: does maschine switch from p1 to p2 in period


            constraints:
                l_[prod]_[period+1] = l_[prod]_[period] + x_[prod]_[period] - d_prod_period
                sum(switch[x][p2][t]) == sum(switch[p2][x][t+1])
                l_[prod]_[period] + x_[prod]_[period] > d_prod_period
                x_prod_period * a_prod + switch_p1_p2_period * st_p1_p2
                quicksum(switch[x][y][t]) == 1
        """

        tHor = int(self.store["Timehorizon"])
        nPr = int(self.store["nProducts"])

        timeRange = range(1, tHor + 1)
        prodRange = range(1, nPr + 1)
        
        # generate Variables
        # lager
        l = {}
        # production
        x = {}
        for t in timeRange:
            for p in prodRange:
                x[p, t] = model.addVar(name="x_%d_%d" % (p, t), vtype="i")
        for t in range(0, tHor + 1):
            for p in prodRange:
                l[p, t] = model.addVar(name="l_%d_%d" % (p, t), vtype="i", obj=float(self.store["h"][p-1]))

        # switch costs
        s = {}
        for t in range(0, tHor+1):
            for p1 in prodRange:
                for p2 in prodRange:
                    if p1 != p2:
                        objective = float(self.store["s"][p1-1][p2-1])
                    else:
                        objective = 0
                    s[p1, p2, t] = model.addVar(name="s_%d_%d_%d" % (p1, p2, t), vtype="b", obj=objective)

        model.modelSense = GRB.MINIMIZE
        model.update()

        for y in model.getVars():
            logging.debug("%s obj %s", y.varName, y.obj)

        # Constraints

        # Initially only allow a single product
        logging.debug("%s == 1", [s[key].varName for key in s if key[2] == 0])
        model.addConstr(quicksum(s[key] for key in s if key[2] == 0) == 1, name="single_switch_" + str(t))

        # Only allow products in each period that actually has been switched to
        for t in timeRange:
            for p in prodRange:
                logging.debug("(%s * %s) == %s", [s[key].varName for key in s if key[2] == t and (key[1] == p or key[0] == p)], x[p, t].varName, x[p, t].varName)
                model.addConstr(quicksum(s[key] for key in s if key[2] == t and (key[1] == p or key[0] == p)) * x[p,t] == x[p,t], name="single_switch_" + str(t))

        for t in timeRange:
            logging.debug('Single switch constraint for ' + str([s[key].varName for key in s if key[2] == t]))
            model.addConstr(quicksum(s[key] for key in s if key[2] == t) == 1, name="single_switch_" + str(t))


            if 1 or t != 1:
                for p in prodRange:
                    logging.debug('valid_switch for ' + str([s[key].varName for key in s if key[2] == (t-1) and key[1] == p]) + " and " + str([s[key].varName for key in s if key[2] == t and key[0] == p]))
                    model.addConstr(quicksum(s[key] for key in s if key[2] == (t-1) and key[1] == p) == quicksum(s[key] for key in s if key[2] == t and key[0] == p), 
                        name="valid_switch_%d_%d" % (p, t))

        # Bedarf periode 0
        for p in range(1, len(self.store["l"])+1):
            logging.debug('initial %s + %d >= %d', x[p, 1].varName, self.store["l"][p-1], self.store["d"][p-1][0])
            model.addConstr(x[p, 1] + self.store["l"][p-1] >= self.store["d"][p-1][0])

        # Bedarf ab periode 1
        for t in range(2, tHor+1):
            for p in prodRange:
                logging.debug('%s + %s >= %d', x[p, t].varName, l[p, t-1].varName, self.store["d"][p-1][t-1])
                model.addConstr(x[p, t] + l[p, t-1] >= self.store["d"][p-1][t-1])

        # Stundenzahl
        for t in timeRange:

            logging.debug("sum {} + sum {} <= {}".format([x[key].varName + "*" + str(self.store["a"][key[0]-1]) for key in x if key[1] == t],
                [s[key].varName + "*" + str(self.store["st"][key[0]-1][key[1]-1]) for key in s if key[2] == t], self.store["K"][t-1]))

            model.addConstr(quicksum(x[key]*self.store["a"][key[0]-1] for key in x if key[1] == t) + quicksum(s[key]*self.store["st"][key[0]-1][key[1]-1] for key in s if key[2] == t) <= self.store["K"][t-1])

        # lager periode 0
        for p in prodRange:
            logging.debug("%s == %s", l[p, 0].varName, self.store["l"][p-1])
            model.addConstr(l[p, 0] == self.store["l"][p-1])
        # lager ab periode 1
        for t in range(1, tHor+1):
            for p in prodRange:
                logging.debug("{} = {} + {} - {}".format(l[p, t].varName, l[p, t-1].varName, x[p, t].varName, self.store["d"][p-1][t-1]))
                model.addConstr(l[p, t] == l[p, t-1] + x[p, t] - self.store["d"][p-1][t-1])

        # solve it
        model.optimize()

        for y in model.getVars():
            if y.x >= 0.001:
                logging.debug("%s = %s cost %d", y.varName, y.x, y.x*y.obj)

        for t in timeRange:
            logging.debug("%s + %s", (["{}[{}] * {}".format(x[key].x, x[key].varName, self.store["a"][key[0]-1]) for key in x if key[1] == t]), ([str(s[key].varName) + "*" + str(self.store["st"][key[0]-1][key[1]-1]) for key in s if key[2] == t and s[key].x >= 0.001]))           

        self.model = model

    def getInstance(self):
        return self.model


def solve(full_path_instance):
    return LotSolver(full_path_instance).getInstance()
