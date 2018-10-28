import sys
import heapq
import copy
import utilities
import grid
import message
import threading
import search_map
import heuristic

class SearchNode:
    def __init__(self, position=search_map.Position(), parent=None):
        self.position = position
        self.parent = parent


class PriorityEntry:
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority


class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, item, priority):
        heapq.heappush(self.queue, PriorityEntry(priority, item))

    def pop(self):
        return heapq.heappop(self.queue)

    def empty(self):
        return len(self.queue) == 0

class AStar:
    @staticmethod
    def parse_result(map, open_list, path_found, message_queue=None):
        # Return result map with with the path from start to end
        result = -1
        correct_path = []
        if path_found:
            result = copy.deepcopy(map.map)
            result[map.start.x][map.start.y] = "S"
            result[map.end.x][map.end.y] = "G"

            for x in range(0, map.size):
                for y in range(0, map.size):
                    if result[x][y] == 1:
                        result[x][y] = "o"
                    elif result[x][y] == 0:
                        result[x][y] = "-"

            node = open_list[-1]
            correct_path.append(node)
            if message_queue != None:
                msg = message.Message(action="PUSH", param=grid.Grid.CORRECT_PATH_ID)
                msg.x = node.position.x
                msg.y = node.position.y
                message_queue.put_nowait(msg)
            node = node.parent
            while node.parent != None:
                correct_path.append(node)
                if message_queue != None:
                    msg = message.Message(action="PUSH", param=grid.Grid.CORRECT_PATH_ID)
                    msg.x = node.position.x
                    msg.y = node.position.y
                    message_queue.put_nowait(msg)
                x = node.position.x
                y = node.position.y
                result[x][y] = "x"
                node = node.parent

            correct_path.append(SearchNode(map.start))
            if message_queue != None:
                msg = message.Message(action="PUSH", param=grid.Grid.CORRECT_PATH_ID)
                msg.x = node.position.x
                msg.y = node.position.y
                message_queue.put_nowait(msg)
            correct_path.reverse()

        if message_queue != None:
            message_queue.put_nowait(message.Message(action="UNLOCK", param=path_found))
        return result, correct_path

    @staticmethod
    @utilities.timer
    def search_map(map, heuristic, epsilon=1, message_queue=None):
        # Create a map for checking if a block is in queue
        check_map = utilities.Utilities.create_matrix(map.size, -1)
        check_map[map.start.x][map.start.y] = 0

        # Run algorithm
        path_found = False
        open_list = []
        queue = PriorityQueue()
        # Lock user input
        if message_queue != None:
            message_queue.put_nowait(message.Message(action="LOCK"))
        # Clear path
        if message_queue != None:
            message_queue.put_nowait(message.Message(action="CLEAR"))
        node = SearchNode(map.start, None)
        queue.push(node, heuristic(map.start, map.end))
        while not queue.empty():
            node = queue.pop()

            # Request drawing
            if message_queue != None:
                pop_message = message.Message(action="PUSH", param=grid.Grid.POP_ID)
                pop_message.x = node.data.position.x
                pop_message.y = node.data.position.y
                message_queue.put_nowait(pop_message)

            node = node.data
            x = node.position.x
            y = node.position.y
            if not map.is_valid(x, y) or map.is_wall(x, y):
                break
            open_list.append(node)

            # If current node is end, stop
            if x == map.end.x and y == map.end.y:
                path_found = True
                break

            g_value = check_map[x][y] + 1
            dxdyrange = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, 1),
                (1, 1),
                (1, 0),
                (1, -1),
                (0, -1),
            ]
            for (dx, dy) in dxdyrange:
                tempx = x + dx
                tempy = y + dy
                # Child is a wall or not valid
                if not map.is_valid(tempx, tempy) or map.is_wall(tempx, tempy):
                    continue
                # Child is already in queue and has smaller g(x)
                if check_map[tempx][tempy] != -1 and check_map[tempx][tempy] <= g_value:
                    continue

                # Otherwise, add child to queue
                check_map[tempx][tempy] = g_value
                child_pos = search_map.Position(tempx, tempy)
                f_value = g_value + heuristic(child_pos, map.end) * epsilon
                queue.push(SearchNode(child_pos, node), f_value)

                # Request drawing
                if message_queue != None:
                    in_queue_message = message.Message(action="PUSH", param=grid.Grid.IN_QUEUE_ID)
                    in_queue_message.x = tempx
                    in_queue_message.y = tempy
                    message_queue.put_nowait(in_queue_message)

        return map, open_list, path_found

class TestPathFinding:
    def __init__(self, inp="", out="", time_input="", time_output=""):
        self.input = inp
        self.output = out
        self.time_input = time_input
        self.time_output = time_output

    @staticmethod
    def run_path_finding(map, heuristic, epsilon=1):
        result, queue, path_found = AStar.search_map(
            map, heuristic, epsilon=epsilon)
        return AStar.parse_result(result, queue, path_found)

    def run(self, heuristic):
        map = search_map.Map()
        map.read_from_file(self.input)

        try:
            with open(self.output, "w") as out:
                result, path = TestPathFinding.run_path_finding(map, heuristic)
                outdata = ""
                if len(path) > 0:
                    outdata += "{}\n".format(len(path))
                    for node in path:
                        outdata += "({},{}) ".format(node.position.x,
                                                     node.position.y)

                    for x in result:
                        if outdata != "":
                            outdata += "\n"
                        for y in x:
                            outdata += str(y) + " "
                else:
                    outdata = "-1"
                out.write(outdata)
        except IOError:
            print("Something went wrong while writing to {}".format(self.output))
        finally:
            out.close()

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        raise Exception("""This program needs at least 2 arguments for input path and output path""")

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    h = heuristic.Heuristic.euclidian_distance
    if len(sys.argv) == 4:
        if sys.argv[3] == "max":
            h = heuristic.Heuristic.max_dx_dy
        elif sys.argv[3] == "min":
            h = heuristic.Heuristic.min_dx_dy

    test = TestPathFinding(input_path, output_path)
    test.run(h)