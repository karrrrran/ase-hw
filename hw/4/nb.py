from sys import path
import os
path.append(os.path.abspath("..") + "\\3")

from hw3 import Tbl, cells, cols, rows, file
from ABCD import Abcd

class NB:
    "Naive Bayes Classifier"
    def __init__(self):
        self.tbl = Tbl()
        self.things = None
        self.m = 2
        self.k = 1
        self.n = -1
    

    def train(self,file_name):
        "Train the model"
        file_contents = cells(cols(rows(file(file_name))))
        for idx, row in enumerate(file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                self.tbl.addRow(row)
                self.n += 1
                class_label = row[self.tbl.col_info["goals"][0]] 
                self.nb_ensure_class_exists(class_label)
                self.things[class].addRow(row)


    def nb_ensure_class_exists(self, class_label):
        "Ensure if 'things' dictionay contains the class"
        if not class_label in self.things:
            self.things[class_label] = Tbl()
            head = self.tbl.tbl_header()
            self.things[class_label].addCol(head)

