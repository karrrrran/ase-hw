from collections import defaultdict
from math import log2
import re
import statistics
from operator import itemgetter
import zipfile
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
    return str


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
    
    def dominates(self, j, goals):
        z = 0.00001
        s1, s2, n = z, z, z+len(goals)
        for goal in goals:
            if isinstance(goal, Num):
                a,b = self.cells[goal.position], j.cells[goal.position]
                a,b = goal.norm(a), goal.norm(b)
                s1 -= 10**(goal.weight * (a-b)/n)
                s2 -= 10**(goal.weight * (b-a)/n)
        return (s1/n - s2/n)

class Col(MyID):
    "Col class for each column in data"

    def __init__(self, column_name, position, weight, rank = 0):
        self.generate_oid()
        self.column_name = column_name
        self.position = position
        self.weight = weight
        self.rank = rank
        self.n = 0
        self.all_values = []


class Num(Col):
    "Num class as a subclass of Col"

    def __init__(self, column_name = "", position = 0, weight = 1):
        super().__init__(column_name, position, weight)
        self.mu = 0     # mean
        self.m2 = 0     # square diff
        self.lo = 10 ** 32
        self.hi = -1 * 10 ** 32
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
        self.delete_value(number)
    
    def delete_from_front(self):
        "Remove a value from front of the list"
        number = self.all_values.pop(0)
        self.delete_value(number)

    def delete_value(self,number):
        if self.n < 2:
            self.n, self.mu, self.m2 = 0, 0, 0
        else:
            self.n -= 1
            d = number - self.mu
            self.mu -= d / self.n
            self.m2 -= d * (number - self.mu)
            self.sd = 0 if self.n < 2 else (self.m2 / (self.n - 1 + 10 ** -32)) ** 0.5
    
    def num_like(self, x):
        "Determines how much Num class likes a symbol"
        var = self.sd**2
        denom = (3.14159*2*var)**0.5
        num   =  2.71828**(-(x-self.mu)**2/(2*var+0.0001))
        return num/(denom + 10**-64)

    def variety(self):
        return self.sd
    
    def xpect(self, second_class):
        total_n = self.n + second_class.n
        return (self.sd*self.n/total_n) + (second_class.sd*second_class.n/total_n)

    def norm(self, val):
        return (val - self.lo) / (self.hi - self.lo + 10**-32)

    def dist(self, val1,val2):
        "Calculate distance between 2 rows"
        norm = lambda z: (z - self.lo) / (self.hi - self.lo + 10**-32)
        if val1 == SYMBOLS.skip:
            if val2 == SYMBOLS.skip: return 1
            val2 = norm(val2)
            val1 = 0 if val2 > 0.5 else 1
        else:
            val1 = norm(val1)
            if val2 == SYMBOLS.skip:
                val2 = 0 if val1 > 0.5 else 1
            else:
                val2 = norm(val2)
        return abs(val1-val2)


class Sym(Col):
    "Sym class as a subclass of Col"

    def __init__(self, column_name = "", position = 0, weight = 1):
        super().__init__(column_name, position, weight)
        self.counts_map = defaultdict(int)
        self.mode = None
        self.most = 0
        self.entropy = None
    
    def add_new_value(self, value):
        "Add new value to column"
        self.all_values.append(value)
        self.counts_map[value] += 1
        self.n += 1
        if self.counts_map[value] > self.most:
            self.most = self.counts_map[value]
            self.mode = value
    
    def delete_from_behind(self):
        "Remove a character from front"
        char = self.all_values.pop()
        self.delete_value(char)

    def delete_from_front(self):
        "Remove a character from front"
        char = self.all_values.pop(0)
        self.delete_value(char)
    
    def delete_value(self, char):
        if self.n < 2:
            self.mode, self.n,self.entropy,self.most = None, 0, None, 0
        else:
            self.n -= 1
            if char == self.mode:
                #change mode
                self.counts_map[char] -= 1
                temp_count = 0
                temp_char = None
                for each in self.counts_map:
                    if self.counts_map[each] > temp_count:
                        temp_count = self.counts_map[each]
                        temp_char = each
                self.mode = temp_char
                self.most = temp_count
            else:
                self.counts_map[char] -= 1

    def calculate_entropy(self):
        "Calculate Entropy"
        entropy = 0
        for key,value in self.counts_map.items():
            if value != 0:
                probability = float(value/self.n)
                entropy -= probability*log2(probability)
        self.entropy = entropy

    def sym_like(self, x, prior, m = 2):
        "Calculates how much a symbol is liked by Sym Class"
        freq = self.counts_map[x] if x in self.counts_map else 0
        return (freq + m*prior) / (self.n + m)

    def test(self):
        "Test Sym Class"
        input_string = "aaaabbc"
        for val in input_string:
            self.add_new_value(val)
        self.calculate_entropy()
        print (round(self.entropy,2))
    
    def variety(self):
        if not self.entropy:
            self.calculate_entropy()
        return self.entropy

    def xpect(self, second_class):
        if not self.entropy:
            self.calculate_entropy()
        if not second_class.entropy:
            second_class.calculate_entropy()
        total_n = self.n + second_class.n
        return (self.entropy*self.n/total_n) + (second_class.entropy*second_class.n/total_n)
    
    def dist(self, val1,val2):
        "Calculate distance between 2 rows"
        if val1 == SYMBOLS.skip and val2 == SYMBOLS.skip: return 1
        if x != y: return 1 
        return 0

class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"

    def __init__(self):
        self.rows = list() #Will hold Row objects for each row
        self.cols = list() #Will hold Num objects for each column
        self.col_info = {'goals': [], 'nums': [], 'syms': [], 'xs' : [], 'negative_weight' : []}

    def dump(self):
        # replaced manual printing with JSON output
        print("Table Object")
        # Single line output to JSON
        print(json.dumps(json.loads(jsonpickle.encode(self)), indent=4, sort_keys=True))
            
    def addCol(self, column):
        for idx,col_name in enumerate(column):
            if bool(re.search(r"[<>$]",col_name)):
                self.col_info['nums'].append(idx)
                if bool(re.search(r"[<]", col_name)):
                    # Weight should be -1 for columns with < in their name
                    self.col_info['negative_weight'].append(idx)
                    self.cols.append(Num(col_name,idx,-1))
                else:
                    self.cols.append(Num(col_name,idx))
            else:
                self.col_info['syms'].append(idx)
                self.cols.append(Sym(col_name,idx))
            if bool(re.search(r"[<>!]",col_name)):
                self.col_info['goals'].append(idx)
            else:
                self.col_info['xs'].append(idx)


    def tbl_header(self):
        return [col.column_name for col in self.cols]

    def read(self, s, type = "string"):
        content = None
        if type == "file":
            content = cells(cols(rows(file(s))))
        else:
            content = cells(cols(rows(fromString(s))))
        for idx, row in enumerate(content):
            if idx == 0:
                # Column names are here
                self.cols = []
                self.addCol(row)
            else:
                self.addRow(row)
    
    def addRow(self, row):
        for i in range(len(self.cols)):
            self.cols[i].add_new_value(row[i])
        self.rows.append(Row(row))

if __name__ == "__main__":
    
    #Test SYM class
    sym = Sym("test_column", 0)
    sym.test()

    #Test TBL class
    s="""
        outlook, ?$temp,  <humid, wind, !play
        rainy, 68, 80, FALSE, yes # comments
        sunny, 85, 85,  FALSE, no
        sunny, 80, 90, TRUE, no
        overcast, 83, 86, FALSE, yes
        rainy, 70, 96, FALSE, yes
        rainy, 65, 70, TRUE, no
        overcast, 64, 65, TRUE, yes
        sunny, 72, 95, FALSE, no
        sunny, 69, 70, FALSE, yes
        rainy, 75, 80, FALSE, yes
        sunny, 75, 70, TRUE, yes
        overcast, 72, 90, TRUE, yes
        overcast, 81, 75, FALSE, yes
        rainy, 71, 91, TRUE, no
    """
    table = Tbl()
    table.read(s)
    table.dump()