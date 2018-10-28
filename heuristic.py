import math

class Heuristic:
    @staticmethod
    def euclidian_distance(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
    
    @staticmethod
    def min_dx_dy(p1, p2):
        dx = abs(p1.x - p2.x)
        dy = abs(p1.y - p2.y)
        return dx if dx < dy else dy

    @staticmethod
    def max_dx_dy(p1, p2):
        dx = abs(p1.x - p2.x)
        dy = abs(p1.y - p2.y)
        return dy if dx < dy else dx