import sys
sys.path.insert(0, r'E:\NCSU drive\Sem 3\ASE\ase-hw\hw\1')
from hw1 import Num

import re

def compiler(x):
    "return something that can compile strings of type x"
    try: int(x); return  int 
    except:
        try: float(x); return  float
        except ValueError: return str

def string(s):
    "read lines from a string"
    for line in s.splitlines(): yield line

def file(fname):
    "read lines from a fie"
    with open(fname) as fs:
        for line in fs: yield line

def zipped(archive,fname):
    "read lines from a zipped file"
    with zipfile.ZipFile(archive) as z:
        with z.open(fname) as f:
            for line in f: yield line

def rows(src, sep= ",", doomed = r'([\n\t\r ]|#.*)'):
    "convert lines into lists, killing whitespace and comments"
    for line in src:
        line = line.strip()
        line = re.sub(doomed, '', line)
        if line:
            yield line.split(sep)

def cells(src):
    "convert strings into their right types"
    oks = None
    for n,cells in enumerate(src):
        if n==0:
            yield cells
        else:
            oks = oks or [compiler(cell) for cell in cells]
            yield [f(cell) for f,cell in zip(oks,cells)]

def fromString(s):
    "putting it all together"
    for lst in cells(rows(string(s))):
        yield lst


class Row:
    "Row class describing each row in data"
    def __init__(self, cells, cooked = [], dom = 0):
        self.cells = cells
        self.cooked = cooked
        self.dom = dom


class Col:
    "Col class for each column in data"
    def __init__(self, col, txt):
        self.col = col
        self.txt = txt


class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"
    def __init__(self):
        self.rows = list()

    def dump(self):
        pass
    
    def read(self, s):
        for row in fromString(s):
            print (row)


if __name__ == "__main__":
    s="""
        $cloudCover, $temp, $humid, $wind,  $playHours
        100,        68,    80,    0,    3   # comments
        0,          85,    85,    0,    0
        0,          80,    90,    10,   0
        60,         83,    86,    0,    4
        100,        70,    96,    0,    3
        100,        65,    70,    20,   0
        70,         64,    65,    15,   5
        0,          72,    95,    0,    0
        0,          69,    70,    0,    4
        80,          75,    80,    0,    3  
        0,          75,    70,    18,   4
        60,         72,    90,    10,   4
        40,         81,    75,    0,    2    
        100,        71,    91,    15,   0
  """
    table = Tbl()
    table.read(s)