#!/usr/bin/env python3
import logging
import matplotlib.pyplot as plt


from runfirehouses import FireSolver

def graphSingleSolution(path):
    solver = FireSolver(path)

    plt.figure(1)
    plt.xlabel("x-Coordinate")
    plt.ylabel("y-Coordinate")
    plt.title('Solution of Group POM_DM')

    def renderSet(inputData, style):
        x_data =  []
        y_data = []
        for inp in inputData:
            x_data.append(inp["x_coord"])
            y_data.append(inp["y_coord"])
        plt.plot(x_data, y_data, style)

    def renderLine(bid, fid, style):
        x_data = []
        y_data = []
        for x in solver.boroughs:
            if x["loc_id"] == bid:
                x_data.append(x["x_coord"])
                y_data.append(x["y_coord"])
        for x in solver.new_firehouses + solver.old_firehouses:
            if x["loc_id"] == fid:
                x_data.append(x["x_coord"])
                y_data.append(x["y_coord"])
        plt.plot(x_data, y_data, style)

    # Render utilized connections
    openedFhs = []
    closedFhs = []

    for x in solver.model.getVars():
        if x.x == 1:
            if x.varName.startswith('x'):
                bid, fid = x.varName.split('_')[1::]
                renderLine(bid, fid, 'k-')
            if x.varName.startswith('open'):
                openedFhs.append(x.varName.split('_')[1])
            if x.varName.startswith('close'):
                closedFhs.append(x.varName.split('_')[1])



    # Plot all locations
    renderSet([x for x in solver.new_firehouses if x["loc_id"] in openedFhs], 'bo')
    renderSet([x for x in solver.old_firehouses if x["loc_id"] not in closedFhs], 'yo')
    renderSet(solver.boroughs, 'ks')

    plt.grid(True)

    plt.savefig(path + '.png')
    #plt.show()
    plt.clf()

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

graphSingleSolution('firedata1.csv')
graphSingleSolution('firedata2.csv')