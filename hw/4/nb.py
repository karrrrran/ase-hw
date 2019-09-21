from sys import path
import os
path.append(os.path.abspath("..") + "\\3")

from hw3 import Tbl, cells, cols, rows, file
from ABCD import Abcd

class NB:

    def __init__(self):
        self.tbl = Tbl()
        self.things = None
        self.m = 2
        self.k = 1
        self.n = -1
