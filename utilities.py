import os
import time
import search_map 
import grid
import functools 

class Utilities:
    @staticmethod
    def create_grid(row_num, col_num, default_value):
        a_grid = []
        for row in range(0, row_num):
            a_row = []
            for col in range(0, col_num):
                item = grid.GridItem()
                item.push(default_value)
                a_row.append(item)
            a_grid.append(a_row)
        return a_grid
    
    @staticmethod
    def create_map(size, default_value):
        matrix = []
        for row in range(size):
            a_row = []
            for col in range(size):
                a_row.append(default_value)
            matrix.append(a_row)
        map = search_map.Map()
        map.map = matrix
        map.size = size
        return map

    @staticmethod
    def create_matrix(size, default_value):
        matrix = []
        for row in range(size):
            a_row = []
            for col in range(size):
                a_row.append(default_value)
            matrix.append(a_row)
        return matrix

def timer(func):
    @functools.wraps(func)
    def timed(*args, **kwargs):
        time_start = time.perf_counter()
        result = func(*args, **kwargs)
        time_end = time.perf_counter()

        timed.time_elapsed = float(time_end - time_start) * 1000
        print("{} runs in  {:.2f} milliseconds".format(func.__name__, timed.time_elapsed))
        
        return result
    return timed