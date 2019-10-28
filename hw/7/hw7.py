from sys import path
import os, random
path.append(os.path.abspath("..") + "\\3")
from hw3 import Num, Sym, Tbl, cells, cols, rows, file
seed=random.seed

def distance(row1, row2, cols):
    d, n, p = 0, 0, 2
    for col in cols:
        n += 1
        d0 = col.dist(row1.cells[col.pos], row2.cells[col.pos])
        d += d0**p
    return d**(1/p) / n**(1/p)      #normalize distance    

def cosine (row1, pt1, pt2, dist, cols):
    return (distance(x, z, cols)**2 + dist**2 - distance(y, z, cols)**2)/(2*dist)

class Hw7:
    def __init__(self, file_name):
        seed(1)
        self.file_contents = cells(cols(rows(file(file_name))))
        self.tbl = Tbl()
        self.parse_file_contents()

    def parse_file_contents(self):
        for idx, row in enumerate(file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                self.tbl.addRow(row)
    
    def get_pivot_points(self, tbl):
        counter = 10
        all_points = []
        while counter > 0:
            counter -= 1
            cols = self.tbl.col_info['xs']
            random_point = random.randint(0,len(tbl.rows)-1)
            max_dist, first_point_idx = 0, None
            for row in range(0,len(tbl.rows)):
                dist = distance(tbl.rows[random_point],tbl.rows[row], cols)
                if dist > max_dist:
                    first_point_idx, max_dist = row, dist
            max_dist, second_point_idx = 0, None
            for row in range(0,len(tbl.rows)):
                dist = distance(tbl.rows[first_point],tbl.rows[row], cols)
                if dist > max_dist:
                    second_point_idx, max_dist = row, dist    
            distance_between_points = dist(tbl.rows[first_point_idx], tbl.rows[second_point_idx], cols)
            all_points.append((first_point_idx, second_point_idx, distance_between_points))
    

if __name__ == '__main__':
    hw7 = Hw7('pom310000.csv')
    # hw7('xomo10000.csv')