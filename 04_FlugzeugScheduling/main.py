#!/usr/bin/env python3
import logging

from runscheduling import solve

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)-5.5s] %(funcName)s : %(message)s")

solver = solve("airland1.txt")
solver2 = solve("airland2.txt")
solver3 = solve("airland3.txt")
solver3 = solve("airland4.txt")
