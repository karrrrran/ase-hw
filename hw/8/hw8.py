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
r= random.randint
seed=random.seed

class TestAuto:
    def __init__(self, file_name):
        seed(1)
        self.file_contents = cells(cols(rows(file(file_name))))
        self.tbl = Tbl()
        self.parse_file_contents()
        self.random_rows = self.get_random_rows()
        self.goals = self.get_goals()
        
    def parse_file_contents(self):
        for idx, row in enumerate(self.file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                self.tbl.addRow(row)
    
    def get_random_rows(self):
        length = len(self.tbl.rows)
        return [self.tbl.rows[r(0, length-1)] for _ in range(100)]
    
    def get_goals(self):
        return [self.tbl.cols[each] for each in self.tbl.col_info['goals']]

    def print_sorted_values(self):
        values = self.sort_rows()
        cols = [each.column_name for each in self.tbl.cols]
        print ("\t" , end = "\t")
        for each in cols:
            print (each, end= "\t")
        print ("")
        for each in values[-4:]:
            print ("best", end = "\t")
            for val in each[1].cells:
                print (val, end = "\t")
            print("")
        print ("")
        for each in values[:4]:
            print ("worst", end = "\t")
            for val in each[1].cells:
                print (val, end = "\t")
            print("")
        
    def sort_rows(self):
        values = []
        for rowi in self.random_rows:
            count = 0
            for rowj in self.random_rows:
                if rowi.dominates(rowj, self.goals) < 0:
                    count += 1
            values.append((count, rowi))
        values.sort(key = lambda x: x[0])
        return values

if __name__ == "__main__":
    t = TestAuto('auto.csv') 
    t.print_sorted_values()