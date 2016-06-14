#!/usr/bin/env python3
import logging

from runlotsizing import LotSolver

#logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

solver = LotSolver("lotData1.txt")
solver2 = LotSolver("lotData2.txt")
solver3 = LotSolver("lotData3.txt")
