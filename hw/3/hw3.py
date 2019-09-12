from collections import defaultdict
from math import log2
import re
import statistics
from operator import itemgetter
import json 

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
        #Skip blanks
        if line:
            yield line.split(sep)

def cells(src,valid_length):
    "convert strings into their right types"
    oks = None
    for n,cells in enumerate(src):
        #If total values are less than total number of column 
        if len(cells) != valid_length:
            print ("E> skipping line due to insufficient data points") 
            continue
        # Skipping '?' valued data points
        oks = [compiler(cell) for cell in cells]
        yield [f(cell) for f,cell in zip(oks,cells)]

def fromString(s):
    "putting it all together"
    all_rows = rows(string(s))
    column_names = next(all_rows)
    valid_columns = [x for x in range(len(column_names)) if '?' not in column_names[x]] 
    yield (itemgetter(*valid_columns)(column_names))
    for lst in cells(all_rows,len(column_names)):
        yield list(itemgetter(*valid_columns)(lst))

class Row:
    "Row class describing each row in data"
    def __init__(self, cells, cooked = [], dom = 0):
        self.cells = cells
        self.cooked = cooked
        self.dom = dom


class Col:
    "Col class for each column in data"
    def __init__(self,column_name, position,weight):
        self.column_name = column_name
        self.position = position
        self.weight = weight


class Num(Col):
    "Num class as a subclass of Col"
    def __init__(self, column_name, position, weight = 1):
        super().__init__(column_name,position, weight)
        self.mean = 0
        self.sd = 0
        self.all_values = []

    def add_new_value(self, number):
        self.all_values.append(number)
        self.update_mean_and_sd()

    def update_mean_and_sd(self):
        self.mean = statistics.mean(self.all_values) if len(self.all_values) > 0 else 0
        self.sd = statistics.stdev(self.all_values) if len(self.all_values) > 1 else 0

    def delete_from_behind(self):
        self.all_values.pop()
        self.update_mean_and_sd()


class Sym(Col):
    "Sym class as a subclass of Col"

    def __init__(self, column_name, position, weight = 1):
        super().__init__(column_name,position, weight)
        self.all_values = []
        self.counts_map = defaultdict(int)
        self.mode = None
        self.most = 0
        self.n = 0
        self.entropy = None
    
    def add_new_value(self, value):
        "Add new value to column"
        self.all_values.append(value)
        self.counts_map[value] += 1
        self.n += 1
        if self.counts_map[value] > self.most:
            self.most = self.counts_map[value]
            self.mode = value
    
    def calculate_entropy(self):
        "Calculate Entropy"
        entropy = 0
        for key,value in self.counts_map.items():
            probability = float(value/self.n)
            entropy -= probability*log2(probability)
        self.entropy = entropy

    def test(self):
        "Test Sym Class"
        input_string = "aaaabbc"
        for val in input_string:
            self.add_new_value(val)
        self.calculate_entropy()
        print (round(self.entropy,2))

class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"
    def __init__(self):
        self.rows = list() #Will hold Row objects for each row
        self.cols = list() #Will hold Num objects for each column
        self.col_info = {'goals': [], 'nums': [], 'syms': [], 'xs' : [], 'negative_weight' : []}

    def dump(self):
        print ("Table Object")
        print ("Columns--")
        for idx,col in enumerate(self.cols):
            print("\t --{0}".format(idx))
            if isinstance(col,Num):
                print ("\t \t Mean: {0}".format(round(col.mean,2)))
                print ("\t \t SD: {0}".format(round(col.sd,2)))
            else:
                print ("\t \t Cnt:")
                for key,value in col.counts_map.items():
                    print ("\t \t \t {0}:{1}".format(key,str(value)))
                print ("\t \t Mode: {0}".format(col.mode))
                print ("\t \t Most: {0}".format(col.most))
                print ("\t \t n: {0}".format(col.n))

            print ("\t \t Column-name: {0}".format(col.column_name))
        print ("\n")
        print ("Rows--")
        for idx,row in enumerate(self.rows):
            print("\t --{0}".format(idx))
            print ("\t \t cells")
            for j,cell in enumerate(row.cells):
                print ("\t \t {0}: {1}".format(j,cell))
            print ("\t \t cooked: {0}".format(row.cooked))
            print ("\t \t dom: {0}".format(row.dom))
        print("\n")
        print("Column Info--")
        for key,value in self.col_info.items():
            print("\t --{0}".format(key))
            if value:
                for each in value:
                    print ("\t \t \t {0}".format(str(each)))    
            

    def read(self, s):
        for idx, row in enumerate(fromString(s)):
            if idx == 0:
                # Column names are here
                self.cols = []
                for idx,col_name in enumerate(row):
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