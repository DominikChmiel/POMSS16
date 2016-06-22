#!/usr/bin/env python3
import logging

from runlotsizing import solve

logging.basicConfig(level='INFO', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

solver = solve("lotData1.txt")
solver2 = solve("lotData2.txt")
solver3 = solve("lotData3.txt")
