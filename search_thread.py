import threading
import math
import heuristic
import astar
import ara

class AStarThread(threading.Thread):
    def __init__(self, map=None, heuristic=heuristic.Heuristic.max_dx_dy, epsilon=1.0, message_queue=None):
        threading.Thread.__init__(self)
        self.started = False
        self.finished = False
        self.result = None
        self.map = map
        self.heuristic = heuristic
        self.epsilon = epsilon
        self.message_queue = message_queue

    def run(self):
        self.started = True
        if self.map == None:
            self.finished = True
            return
        raw_res = astar.AStar.search_map(self.map, self.heuristic, self.epsilon, self.message_queue)
        self.result = astar.AStar.parse_result(*raw_res, message_queue=self.message_queue)
        self.finished = True

class ARAThread(threading.Thread):
    def __init__(self, map=None, heuristic=heuristic.Heuristic.euclidian_distance, limit=math.inf, epsilon=5.0, message_queue=None):
        threading.Thread.__init__(self)
        self.started = False
        self.finished = False
        self.result = None
        self.map = map
        self.heuristic = heuristic
        self.time_limit = limit
        self.epsilon = epsilon
        self.message_queue = message_queue

    def run(self):
        self.started = True
        if self.map == None:
            self.finished = True
            return

        self.result = ara.ARA.search_map(self.map, self.heuristic, self.time_limit, self.epsilon, self.message_queue)
        self.finished = True