from sys import path
import os
path.append(os.path.abspath("..") + "\\3")

from hw3 import Tbl, cells, cols, rows, file
from ABCD import Abcd

class ZeroR:

    def __init__(self):
        self.tbl = Tbl()
        self.abcd = Abcd()

    def zeroRTrain(self, file_name):
        file_contents = cells(cols(rows(file(file_name))))
        for idx, row in enumerate(file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                self.tbl.addRow(row)
    

z = ZeroR()
z.zeroRTrain("weathernon.csv")
