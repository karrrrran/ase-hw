from sys import path
from math import log
import json, jsonpickle, random, re, os
path.append(os.path.abspath("..") + "\\3")
path.append(os.path.abspath("..") + "\\5")
path.append(os.path.abspath("..") + "\\6")
path.append(os.path.abspath("..") + "\\7")
from hw3 import Row, Col, Num, Sym, cells, cols, rows, file, fromString
from utils import same, first, last, ordered, DIVISION_UTILS
from div2 import Div2, column_name_fn
from hw6 import Tbl, pretty_print2
from collections import defaultdict
from hw7 import Hw7
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

# defined exclusively for leaf nodes coming from HW7
def dominates(c1, c2, goals):
    z = 0.00001
    s1, s2, n = z,z,z+len(goals)
    for idx, goal in enumerate(goals):
        if isinstance(goal, Num):
            a,b = c1.leaves[idx].mu, c2.leaves[idx].mu
            a,b = goal.norm(a), goal.norm(b)
            s1 -= 10**(goal.weight * (a-b)/n)
            s2 -= 10**(goal.weight * (b-a)/n)
    return (s1/n - s2/n)

# defined exclusively for leaf nodes coming from HW7
def distance(col1, col2, goals):
    d, n, p = 0, 0, 2
    for idx, col in enumerate(goals):
        n += 1
        d0 = None
        if isinstance(col, Num):
            d0 = col.dist(col1.leaves[idx].mu, col2.leaves[idx].mu)
        else:
            d0 = col.dist(col1.leaves[idx].mode, col2.leaves[idx].mode)
        d += d0**p
    return d**(1/p) / n**(1/p)      #normalize distance    

def envy_sets_step4_5():
    rp_obj = Hw7('auto.csv')
    centroids = rp_obj.leaf_nodes
    envy_nodes_map = defaultdict(list)
    closest_envy_nodes = []
    goals = [rp_obj.tbl.cols[each] for each in rp_obj.tbl.col_info['goals']]
    for c1 in centroids:
        for c2 in centroids:
            if dominates(c1, c2, goals) > 0:
                envy_nodes_map[c1].append(c2)

    for c1 in envy_nodes_map.keys():
        min_dist, most_envy = float('inf'), None
        for c2 in envy_nodes_map[c1]:
            dist = distance(c1,c2,goals)
            if dist < min_dist:
                min_dist = dist
                most_envy = c2 
        closest_envy_nodes.append((c1, most_envy))

    for idx,val in enumerate(closest_envy_nodes):
        new_tbl = Tbl()
        cols = [col.column_name for col in val[0].tbl.cols]
        cols.append('!$new_class')
        new_tbl.addCol(cols)
        for each in val[0].tbl.rows:
            cells = each.cells
            cells.append(0)
            new_tbl.addRow(cells)
        
        for each in val[1].tbl.rows:
            cells = each.cells
            cells.append(1)
            new_tbl.addRow(cells)
        try:
            new_tbl.tree()
            print ("TREE FOR ONE OF THE CLUSTERS and its ENVY CLUSTER")
            pretty_print2(new_tbl.tree_result)
            print ("-----------------------------------------------------------")
        except:
            pass


if __name__ == "__main__":
    # t = TestAuto('auto.csv') 
    # t.print_sorted_values()
    envy_sets_step4_5()