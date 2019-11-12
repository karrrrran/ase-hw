from sys import path
from math import log
import json, jsonpickle, random, re, os
path.append(os.path.abspath("..") + "\\3")
path.append(os.path.abspath("..") + "\\5")
from hw3 import Row, Col, Num, Sym, cells, cols, rows, file, fromString
from utils import same, first, last, ordered, DIVISION_UTILS
from div2 import Div2, column_name_fn
r= random.random
seed=random.seed


def tree_result(low, high, n, text, kids):
    return {
        "low" : low,
        "high" : high,
        "n" : n,
        "text" : text,
        "kids": kids,
    }

def leaf_result(classval, rows):
    if classval == 'p':
        classval = 'tested_positive'
    if classval == 'n':
        classval = 'tested_negative'
    return {
        'val' : classval,
        'n' : rows
    }

class Tbl:
    "Table class for driving the tables comprising of Rows and Cols"
    def __init__(self):
        self.rows = list() #Will hold Row objects for each row
        self.cols = list() #Will hold Num objects for each column
        self.col_info = {'goals': [], 'nums': [], 'syms': [], 'xs' : [], 'negative_weight' : []}
        self.tree_result = None


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
    

    def tree(self):
        class_index = self.col_info["goals"][0]
        class_type = Sym if class_index in self.col_info["syms"] else Num
        func1 = lambda row: row.cells
        data = list(map(func1, self.rows))
        # for row in data:
        #     if row[class_index] == "tested_positive":
        #         row[class_index] = 'p'
        #     else:
        #         row[class_index] = 'n'
        self.tree_result = self.get_tree(data, class_index,class_type, 0)
    

    def get_tree(self, data_rows, class_index, class_type, level):
        if len(data_rows) >= DIVISION_UTILS.minObs:
            #Find the best column to split
            low, cut, column = 10**32, None, None
            column_types = []
            for col in self.cols:
                if isinstance(col,Num):
                    column_types.append(Num)
                else:
                    column_types.append(Sym)
            for col in self.cols:
                if col.position == class_index:
                    continue
                x = Div2(data_rows, col.position, class_index, column_types, column_name_fn)
                cut1, low1 = x.cut, x.best
                if cut1 and low1:
                    if low1 < low:
                        cut, low, column = cut1, low1, col
            #If found a suitable cut
            if cut:
                #Split data on best column and call tree for both halves.
                func = lambda row: row.cells
                return [tree_result(low, high, len(kids), column.column_name, self.get_tree(kids, class_index, class_type, level + 1)) for low,high, kids in self.split(data_rows, cut, column)]                        
        return leaf_result(data_rows[len(data_rows)//2][class_index], len(data_rows))


    def split(self, data_rows, cut, column):
        left_half,low = data_rows[:cut],data_rows[cut][column.position]
        right_half,high = data_rows[cut:], data_rows[cut+1][column.position]
        return [(-float('inf'), low, left_half),(high, float('inf'), right_half)]


def pretty_print(tree, level = 0):
    for _ in range(level):
            print ("| ", end = " ")
    print ("{0} = {1}...{2}".format(tree['text'], tree['low'], tree['high']), end = " ")
    if not isinstance(tree['kids'], list):
        print ("{0} ({1})".format(tree['kids']['val'],tree['kids']['n']))
    else:
        for each in tree['kids']:
            print ("")
            pretty_print(each, level + 1)
            
def pretty_print2(tree, level = 0):
    if isinstance(tree, list):
        for each in tree:
            pretty_print2(each, level)
    else:
        for _ in range(level):
            print ("| ", end = " ")
        print ("{0} = {1}...{2}".format(tree['text'], tree['low'], tree['high']), end = " ")        
        if not isinstance(tree['kids'], list):
            print ("{0} ({1})".format(tree['kids']['val'],tree['kids']['n']))
        else:
            for each in tree['kids']:
                print ("")
                pretty_print2(each, level + 1)
            


if __name__ == "__main__":
    
    # file_name = "../4/diabetes.csv"
    file_name = "auto.csv"
    file_contents = cells(cols(rows(file(file_name))))
    table = Tbl()
    for idx, row in enumerate(file_contents):
        if idx == 0:
            table.addCol(row)
        else:
            table.addRow(row)
    table.tree()
    pretty_print2(table.tree_result)
    # for each in table.tree_result:
    #     pretty_print(each)