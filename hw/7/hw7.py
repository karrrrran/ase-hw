from sys import path
import os, random, math
from collections import defaultdict
path.append(os.path.abspath("..") + "\\3")
path.append(os.path.abspath("..") + "\\6")
from hw3 import Num, Sym,Col, cells, cols, rows, file
from hw6 import Tbl
seed=random.seed

def distance(row1, row2, cols):
    d, n, p = 0, 0, 2
    for col in cols:
        n += 1
        d0 = col.dist(row1.cells[col.position], row2.cells[col.position])
        d += d0**p
    return d**(1/p) / n**(1/p)      #normalize distance    

def cosine (x, y, z, dist, cols):
    return (distance(x, z, cols)**2 + dist**2 - distance(y, z, cols)**2)/(2*dist)


class RPTree:
    def __init__(self):
        self.children = []
        self.leaves = []
        self.tbl = None
        self.level = 0
        self.isRoot = False
        self.splitCount = 0

def print_tree(root):
    if not root.isRoot:
        for _ in range(root.level):
            print ("|. ", end =" ")
    print (root.splitCount)
    if len(root.children) == 0:
        for _ in range(root.level-1):
            print ("|. ", end =" ")
        for col in root.leaves:
            print (col.column_name + " = ", end =" ")
            if (isinstance(col, Num)):
                print ("{0} ({1})".format(col.mu, col.sd), end =" ")
            else:
                print ("{0} ({1})".format(col.mode, col.entropy), end =" ")
        print ("")
    else:
        for each in root.children:
            print_tree(each)
    if root.isRoot:
        for col in root.leaves:
            print (col.column_name + " = ", end =" ")
            if (isinstance(col, Num)):
                print ("{0} ({1})".format(col.mu, col.sd), end =" ")
            else:
                print ("{0} ({1})".format(col.mode, col.entropy), end =" ")

class Hw7:
    def __init__(self, file_name):
        seed(1)
        self.leaf_nodes = []
        self.file_contents = cells(cols(rows(file(file_name))))
        self.tbl = Tbl()
        self.parse_file_contents()
        self.tree = self.split(self.tbl,0)
        
    def parse_file_contents(self):
        for idx, row in enumerate(self.file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                self.tbl.addRow(row)
    
    def split(self, tbl,level):
        node = RPTree()
        if (len(tbl.rows) < 2* pow(len(self.tbl.rows),1/2)):
            for each in tbl.col_info['goals']:
                node.leaves.append(tbl.cols[each])
            node.level = level
            node.tbl = tbl
            node.splitCount = len(tbl.rows)
            self.leaf_nodes.append(node)
            return node
        else:
            best_tuple, best_points = self.best_pivot_points(tbl)
            left_tbl = Tbl()
            right_tbl = Tbl()
            left_tbl.addCol([col.column_name for col in tbl.cols])
            right_tbl.addCol([col.column_name for col in tbl.cols])
            for idx, each in enumerate(tbl.rows):
                if idx in best_points:
                    right_tbl.addRow(each.cells)
                else:
                    left_tbl.addRow(each.cells)
            splitCount = len(left_tbl.rows) + len(right_tbl.rows)
            node.children.append(self.split(left_tbl,level + 1))
            node.children.append(self.split(right_tbl, level + 1))
            node.splitCount = splitCount
            node.level = level
            return node

    def fast_map(self, tbl):
        cols = [tbl.cols[col] for col in tbl.col_info['xs']]
        random_point = random.randint(0,len(tbl.rows)-1)
        first_pivot_pts = []
        for row in range(0,len(tbl.rows)):
            dist = distance(tbl.rows[random_point],tbl.rows[row], cols)
            first_pivot_pts.append((row, dist))
        first_pivot_pts.sort(key = lambda x: x[1])
        first_pivot_idx = first_pivot_pts[math.floor(len(first_pivot_pts)*0.9)][0]    
        second_pivot_pts = []
        for row in range(0,len(tbl.rows)):
            dist = distance(tbl.rows[first_pivot_idx],tbl.rows[row], cols)
            second_pivot_pts.append((row, dist))
        second_pivot_pts.sort(key = lambda x: x[1])
        second_pivot_idx = second_pivot_pts[math.floor(len(second_pivot_pts)*0.9)][0]
        dist = second_pivot_pts[math.floor(len(second_pivot_pts)*0.9)][1]
        return (first_pivot_idx, second_pivot_idx, dist)
    
    def best_pivot_points(self,tbl):
        counter = 10
        initial = len(tbl.rows)
        left_split, right_split = 0,0
        best_tuple = None
        best_points = None
        while counter > 0:
            counter -= 1
            pivot_tuple = self.fast_map(tbl)
            all_list = []
            cols = [tbl.cols[col] for col in tbl.col_info['xs']]
            for row in range(0,len(tbl.rows)):
                dist = cosine(tbl.rows[pivot_tuple[0]], tbl.rows[pivot_tuple[1]], tbl.rows[row], pivot_tuple[2],cols)
                all_list.append((row,dist))
            all_list.sort(key = lambda x: x[1])
            median_distance = None
            length = len(all_list)
            index = (length - 1) // 2
            if (length % 2):
                median_distance = all_list[index][1]
            else:
                median_distance = (all_list[index][1] + all_list[index + 1][1])/2.0
        
            pointset = set()
            for point in all_list:
                if point[1] < median_distance:
                    pointset.add(point[0])
            
            right = abs(len(pointset) - (length - len(pointset)))
            if right < initial:
                initial = right
                left_split = len(pointset)
                right_split = length - len(pointset)
                best_points = pointset
                best_tuple = pivot_tuple
        
        return best_tuple, best_points

if __name__ == '__main__':
    # hw7 = Hw7('pom310000.csv')
    hw7 = Hw7('xomo10000.csv')
    print_tree(hw7.tree)