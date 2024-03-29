from sys import path
import os
path.append(os.path.abspath("..") + "\\3")

from hw3 import Tbl, cells, cols, rows, file
from ABCD import Abcd

class ZeroR:
    "ZeroR classifier"
    def __init__(self):
        self.tbl = Tbl()
        self.abcd = Abcd()
        self.wait = 2

    def train(self, file_name):
        "Train ZeroR model"
        file_contents = cells(cols(rows(file(file_name))))
        for idx, row in enumerate(file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                if idx > self.wait:
                    #Classify the data point
                    got = self.classify() #predicted label
                    want = row[self.tbl.col_info["goals"][0]] #true label
                    self.abcd.abcd1(want,got)
                self.tbl.addRow(row)


    def classify(self):
        "Classify new data point"
        return self.tbl.cols[self.tbl.col_info["goals"][0]].mode


if __name__ == "__main__":

    z1 = ZeroR()
    print ("#--- zerorok ---------------------")
    print ("weathernon")
    z1.train("weathernon.csv")
    z1.abcd.abcd_report()
    print ("\n")
    z2 = ZeroR()
    print ("diabetes")
    z2.train("diabetes.csv")
    z2.abcd.abcd_report()