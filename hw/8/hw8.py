from sys import path
from math import log
import json, jsonpickle, random, re, os
path.append(os.path.abspath("..") + "\\3")
path.append(os.path.abspath("..") + "\\5")
path.append(os.path.abspath("..") + "\\6")
from hw3 import Row, Col, Num, Sym, cells, cols, rows, file, fromString
from utils import same, first, last, ordered, DIVISION_UTILS
from div2 import Div2, column_name_fn
from hw6 import Tbl
r= random.random
seed=random.seed

