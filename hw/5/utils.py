from sys import path
import os
from math import log
path.append(os.path.abspath("..") + "\\3")
from hw3 import SYMBOLS

def last(arr):
    "Returns last element from given list"
    return arr[-1]

def first(arr):
    "Returns first element from given list"
    return arr[0]

def same(num):
    "Right now returns same number"
    return num

def ordered(num_list, key):
    "Sort elements in array at the same time ignore 'Skip' characters"
    return [num_list[x] for x in range(len(num_list)) if SYMBOLS.skip not in key(x)]

class DIVISION_UTILS:
    trivial = 1.025
    cohen = 0.3
    minimum = 0.5