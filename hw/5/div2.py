from sys import path
import os
from math import log
path.append(os.path.abspath("..") + "\\3")
from hw3 import Num, Sym
from utils import same, first, last, ordered, DIVISION_UTILS
import random
r= random.random
seed=random.seed

class Div2:
    "Part 1 of splitting elements in List"
    def __init__(self,num_list, column_x, column_y, column_types, column_name_fn, key_fn = same, recursive = True):
        self.column_types = column_types
        self.column_name_fn = column_name_fn    #Part of the reason to use this is to check the column name in order to skip the column
        self.key_fn = key_fn    
        self.num_list = ordered(num_list, key = column_name_fn, index = column_x)
        self.b4 = [class_type(column_name_fn(idx),idx) for idx,class_type in enumerate(self.column_types)]
        for row in self.num_list:
            for idx, val in enumerate(row):
                self.b4[idx].add_new_value(val)
        self.x = column_x   #column index
        self.y = column_y   #column index
        self.step = int(len(self.num_list))**DIVISION_UTILS.minimum
        self.gain = 0
        self.start = first(self.b4[self.y].all_values)
        self.stop = last(self.b4[self.y].all_values)
        self.ranges = []    #the generated ranges
        self.epsilon = self.b4[self.y].variety()
        self.epsilon *= DIVISION_UTILS.cohen
        low = 1
        high = self.b4[self.y].n
        self.best, self.cut = None, None
        if recursive:
            self.__split(1,low,high,self.b4)
        else:
            self.best, self.cut = self.__single_split(low,high,self.b4)
        self.gain /= self.b4[self.y].n
    
    def __split(self,rank,low,high,b4):
        "Find a split between low and high, then recurse on each split."
        best, cut = self.__single_split(low, high, b4)
        if cut:
            low_b4 = [class_type(self.column_name_fn(idx),idx) for idx,class_type in enumerate(self.column_types)]
            high_b4 = [class_type(self.column_name_fn(idx),idx) for idx,class_type in enumerate(self.column_types)]
            for each in range(len(low_b4)):
                for x in range(low,cut):
                    low_b4[each].add_new_value(self.b4[each].all_values[x])
            for each in range(len(high_b4)):
                for x in range(cut,high):
                    high_b4[each].add_new_value(self.b4[each].all_values[x])
            rank = self.__split(rank,low,cut,low_b4) + 1
            rank = self.__split(rank,cut,high,high_b4)
        else:
            self.gain += b4[self.y].n*b4[self.y].variety()
            b4[self.x].rank = rank
            b4[self.y].rank = rank
            self.ranges.append(b4)
        return rank

    def __single_split(self, low, high, b4):
        left = dict()
        right = dict()
        best = b4[self.y].variety()
        cut = None
        left[self.x] = self.column_types[self.x]()
        left[self.y] = self.column_types[self.y]()
        right[self.x] = self.column_types[self.x]()
        right[self.y] = self.column_types[self.y]()
        for each in range(low,high):
            right[self.x].add_new_value(self.b4[self.x].all_values[each])
            right[self.y].add_new_value(self.b4[self.y].all_values[each])
        for j in range(low, high):
            left[self.x].add_new_value(self.b4[self.x].all_values[j])
            left[self.y].add_new_value(self.b4[self.y].all_values[j])
            right[self.x].delete_value(self.b4[self.x].all_values[j])
            right[self.y].delete_value(self.b4[self.y].all_values[j])
            if left[self.y].n >= self.step:
                if right[self.y].n >= self.step:
                    now = self.key_fn(self.b4[self.y].all_values[j-1])
                    after = self.key_fn(self.b4[self.y].all_values[j])
                    if now == after: continue
                    xpect = None
                    if isinstance(self.b4[self.y],Sym):
                        if abs(ord(right[self.y].mode)-ord(left[self.y].mode)) >= self.epsilon:
                            if ord(after) - ord(self.start) >= self.epsilon:
                                if ord(self.stop) - ord(now) >= self.epsilon:
                                    xpect = left[self.y].xpect(right[self.y])
                    else:
                        if abs(right[self.y].mu-left[self.y].mu) >= self.epsilon:
                            if after - self.start >= self.epsilon:
                                if self.stop - now >= self.epsilon:
                                    xpect = left[self.y].xpect(right[self.y])
                    if xpect:
                        if xpect*DIVISION_UTILS.trivial < best:
                            best,cut = xpect, j
        return best, cut


def num(i):
    if i<0.4: return [i,     r()*0.1]
    if i<0.6: return [i, 0.4+r()*0.1]
    return [i, 0.8+r()*0.1]

def x():
    n = 5
    seed(1)
    return  [      r()*0.05 for _ in range(n)] + \
        [0.2 + r()*0.05 for _ in range(n)] +  \
        [0.4 + r()*0.05 for _ in range(n)] +   \
        [0.6 + r()*0.05 for _ in range(n)] +    \
        [0.8 + r()*0.05 for _ in range(n)]

def xnum():
    return  [num(one) for one in x()]


def column_name_fn(x):
    return ""


def roundoff(x):
    return round(x,5)


def xsym():
    return  [sym(one) for one in x()] * 5


def sym(i):
    if i<0.4: return [i, "a"]
    if i<0.6: return [i, "b"]
    return [i, "c"]


def y():
    seed(1)
    n = 5
    return  [      r()*0.05 for _ in range(n)] + \
          [0.2 + r()*0.05 for _ in range(n)] +  \
          [0.4 + r()*0.05 for _ in range(n)] +   \
          [0.6 + r()*0.05 for _ in range(n)] +    \
          [0.8 + r()*0.05 for _ in range(n)]


if __name__ == "__main__":

    num_list = xnum()
    # num_list = xsym()
    column_types = [Num,Num]
    div2 = Div2(num_list,0,1,column_types,column_name_fn)
    for idx,obj in enumerate(div2.ranges):
        if isinstance(obj[1],Num):
            print ("{0} | x.n: {1} \t  x.lo: {2} \t x.hi: {3} | y.lo: {4} \t y.hi: {5}".format(idx+1, obj[0].n, roundoff(obj[0].lo), roundoff(obj[0].hi),roundoff(obj[1].lo), roundoff(obj[1].hi)))
        else:
            obj[1].calculate_entropy()
            print ("{0} | x.n: {1} \t  x.lo: {2} \t x.hi: {3} | y.mode: {4} \t y.ent: {5}".format(idx+1, obj[0].n, roundoff(obj[0].lo), roundoff(obj[0].hi),obj[1].mode, roundoff(obj[1].entropy)))        
    # div2 = Div2(num_list,0,1,column_types,column_name_fn, recursive= False)
    # print (div2.best, div2.cut)