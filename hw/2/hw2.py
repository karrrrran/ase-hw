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
    def __init__(self,column_name, position):
        self.column_name = column_name
        self.position = position


class Num(Col):
    "Num class as a subclass of Col"
    def __init__(self, column_name, position):
        super().__init__(column_name,position)
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


class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"
    def __init__(self):
        self.rows = list() #Will hold Row objects for each row
        self.cols = list() #Will hold Num objects for each column

    def dump(self):
        print ("Table Object")
        print ("Columns--")
        for idx,col in enumerate(self.cols):
            print("\t --{0}".format(idx))
            print ("\t \t Mean: {0}".format(round(col.mean,2)))
            print ("\t \t SD: {0}".format(round(col.sd,2)))
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

    
    def read(self, s):
        for idx, row in enumerate(fromString(s)):
            if idx == 0:
                # Column names are here
                self.cols = [Num(x,i) for i,x in enumerate(row)]
            else:
                for i in range(len(self.cols)):
                    self.cols[i].add_new_value(row[i])
                self.rows.append(Row(row))


if __name__ == "__main__":
    s="""
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
        50,          75,    80,    0,    60
        0,          75,    70,    18,   4
        60,         72,
        40,         81,    75,    0,    2
        100,        71,    91,    15,   0
  """
    table = Tbl()
    table.read(s)
    table.dump()