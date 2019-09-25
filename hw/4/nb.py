from sys import path
import os
from math import log
path.append(os.path.abspath("..") + "\\3")


from hw3 import Tbl, cells, cols, rows, file
from ABCD import Abcd

class NB:
    "Naive Bayes Classifier"
    def __init__(self):
        self.tbl = Tbl()
        self.things = dict()
        self.m,self.k,self.n,self.wait = 2,1,-1,19
        self.abcd = Abcd()

    def train(self,file_name):
        "Train the model"
        file_contents = cells(cols(rows(file(file_name))))
        for idx, row in enumerate(file_contents):
            if idx == 0:
                self.tbl.addCol(row)
            else:
                if idx > self.wait:
                    #Classify the data point
                    got = self.classify(row) #predicted label
                    want = row[self.tbl.col_info["goals"][0]] #true label
                    self.abcd.abcd1(want,got)
                self.n += 1
                self.tbl.addRow(row)
                class_label = row[self.tbl.col_info["goals"][0]] 
                self.nb_ensure_class_exists(class_label)
                self.things[class_label].addRow(row)


    def nb_ensure_class_exists(self, class_label):
        "Ensure if 'things' dictionay contains the class"
        if class_label not in self.things:
            self.things[class_label] = Tbl()
            head = self.tbl.tbl_header()
            self.things[class_label].addCol(head)


    def classify(self,row):
        most = -10**64
        guess = ""
        for class_label in self.things:
            guess = class_label if guess == "" else guess
            like = self.bayes_theorem(row, self.things[class_label])
            if like > most:
                most = like
                guess = class_label
        return guess

    def bayes_theorem(self, row, thing):
        like = prior = len(thing.rows) + self.k / (self.n + self.k*len(self.things))
        like = log(like)
        for c in thing.col_info["xs"]:
            if c in thing.col_info["nums"]:
                like += log(thing.cols[c].num_like(row[c]))
            else:     
                like += log(thing.cols[c].sym_like(row[c], prior, self.m))
        return like

if __name__ == "__main__":

    nb1 = NB()
    nb1.wait = 3
    print ("#--- nbok ---------------------")
    print ("weathernon")
    nb1.train("weathernon.csv")
    nb1.abcd.abcd_report()
    print ("\n")
    nb2 = NB()
    print ("diabetes")
    nb2.train("diabetes.csv")
    nb2.abcd.abcd_report()