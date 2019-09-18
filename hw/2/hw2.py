# part of this code has been inspired from code shared by Rui Shu on class slack channel

import re
import statistics
import zipfile
from operator import itemgetter
import jsonpickle
import json
import sys


class SYMBOLS:
    sep = ","
    num = "$"
    less = "<"
    more = ">"
    skip = "?"
    doomed = r'([\n\t\r ]|#.*)'


def compiler(x):
    "return something that can compile strings of type x"
    """return something that can compile strings"""
    def num(z):
        f = float(z)
        i = int(f)
        return i if i == f else f

    for c in [SYMBOLS.num, SYMBOLS.less, SYMBOLS.more]:
        if c in x:
            return num


def string(s):
    "read lines from a string"
    for line in s.splitlines(): yield line


def file(fname):
    "read lines from a fie"
    with open(fname) as fs:
        for line in fs: yield line


def zipped(archive, fname):
    "read lines from a zipped file"
    with zipfile.ZipFile(archive) as z:
        with z.open(fname) as f:
            for line in f: yield line


def rows(src, sep=SYMBOLS.sep, doomed=SYMBOLS.doomed):
    "convert lines into lists, killing whitespace and comments"
    linesize = None
    for n, line in enumerate(src):
        line = line.strip()
        line = re.sub(doomed, '', line)
        if line:
            line = line.split(sep)
            # update the linesize for first time
            if linesize is None:
                linesize = len(line)

            # skip line if it doesn't match size
            if len(line) == linesize:
                yield line
            else:
                print("E> skipping line %s" % n)


def cols(src):
    "skip columns whose name contains '?'"
    valid_cols = None
    for cells in src:
        if valid_cols is None:  # Do this just for the first row
            valid_cols = [n for n, cell in enumerate(cells) if not SYMBOLS.skip in cell]
        yield [cells[n] for n in valid_cols]


def cells(src):
    "convert strings into their right types"
    one = next(src)
    fs = [None] * len(one)  # [None, None, None, None]
    yield one  # the first line

    def ready(n, cell):
        if cell == SYMBOLS.skip:
            return cell  # skip over '?'
        fs[n] = fs[n] or compiler(one[n])  # ensure column 'n' compiles
        return fs[n](cell)  # compile column 'n'

    for _, cells in enumerate(src):
        yield [ready(n, cell) for n, cell in enumerate(cells)]


def fromString(input_str):
    "read lines fro string"
    for line in input_str.splitlines():
        yield line


class MyID:
    oid = 0

    def generate_oid(self):
        MyID.oid += 1
        self.oid = MyID.oid
        return self.oid


class Row(MyID):
    "Row class describing each row in data"

    def __init__(self, cells, cooked=[], dom=0):
        self.generate_oid()
        self.cells = cells
        self.cooked = cooked
        self.dom = dom


class Col(MyID):
    "Col class for each column in data"

    def __init__(self, column_name, position):
        self.generate_oid()
        self.column_name = column_name
        self.position = position


class Num(Col):
    "Num class as a subclass of Col"

    def __init__(self, column_name, position):
        super().__init__(column_name, position)
        self.n = 0
        self.mu = 0     # mean
        self.m2 = 0     # square diff
        self.lo = 10 ** 32
        self.hi = -1 * 10 ** 32
        self.all_values = []
        self.sd = 0

    def add_new_value(self, number):
        "Add new value to the list and update the paramaters"
        self.all_values.append(number)
        if number < self.lo:
            self.lo = number
        if number > self.hi:
            self.hi = number

        self.n += 1
        d = number - self.mu
        self.mu += d / self.n
        self.m2 += d * (number - self.mu)
        self.sd = 0 if self.n < 2 else (self.m2 / (self.n - 1 + 10 ** -32)) ** 0.5

    def delete_from_behind(self):
        "Remove a value from behind the list"
        number = self.all_values.pop()
        if self.n < 2:
            self.n, self.mu, self.m2 = 0, 0, 0
        else:
            self.n -= 1
            d = number - self.mu
            self.mu -= d / self.n
            self.m2 -= d * (number - self.mu)
            self.sd = 0 if self.n < 2 else (self.m2 / (self.n - 1 + 10 ** -32)) ** 0.5


class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"

    def __init__(self):
        self.rows = list()  # Will hold Row objects for each row
        self.cols = list()  # Will hold Num objects for each column
        self.oid = 0

    def dump(self):
        # replaced manual printing with JSON output
        print("Table Object")
        # Single line output to JSON
        print(json.dumps(json.loads(jsonpickle.encode(self)), indent=4, sort_keys=True))

    def read(self, inputfile):
        for idx, row in enumerate(cells(cols(rows(fromString(inputfile))))):
            print(row)
            if idx == 0:
                # Column names are here
                self.cols = [Num(x, i) for i, x in enumerate(row)]
            else:
                for i in range(len(self.cols)):
                    self.cols[i].add_new_value(row[i])
                self.rows.append(Row(row))


if __name__ == "__main__":
    s = """
        $cloudCover, $temp, ?$humid, <wind,  $playHours
        100,        68,    80,    0,    3   # comments
        0,          85,    85,    0,    0

        0,          80,    90,    10,   0
        60,         83,    86,    0,    4
        100,        70,    96,    0,    3
        100,        65,    70,    20,   0
        70,         64,    65,    15,   5
        0,          72,    95,    0,    0
        0,          69,    70,    0,    4
        0,          75,    80,    0,    0
        0,          75,    70,    18,   4
        60,         72,
        40,         81,    75,    0,    2
        100,        71,    91,    15,   0
  """

    s2 = """
    $cloudCover, $temp, $humid, $wind,  $playHours
  100,         68,    80,     0,      3   
  0,           85,    85,     0,      0
  0,           80,    90,     10,     0
  60,          83,    86,     0,      4
  100,         70,    96,     0,      3
  100,         65,    70,     20,     0
  70,          64,    65,     15,     5
  0,           72,    95,     0,      0
  0,           69,    70,     0,      4
  80,          75,    80,     0,      3
  0,           75,    70,     18,     4
  60,          72,    83,     15,     5
  40,          81,    75,     0,      2
  100,         71,    91,     15,     0
    """
    table = Tbl()
    table.read(s)
    table.dump()
