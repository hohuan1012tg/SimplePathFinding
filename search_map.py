class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Map:
    def __init__(self):
        self.size = 0
        self.map = []
        self.start = Position()
        self.end = Position()

    def read_from_file(self, file_name):
        try:
            with open(file_name, "r") as file:
                try:
                    # Read all data
                    data = file.read().strip().split()
                    self.size = int(data[0])

                    # Read start point position
                    self.start.x = int(data[1])
                    self.start.y = int(data[2])

                    # Read end point position
                    self.end.x = int(data[3])
                    self.end.y = int(data[4])

                    # Read map data
                    data = data[5:]
                    for x in range(0, self.size):
                        for y in range(0, self.size):
                            if y == 0:
                                self.map.append([])
                            block = int(data[x * self.size + y])
                            if block < 0 or block > 1:
                                raise Exception(
                                    "Value in map must be either 0 or 1")
                            self.map[x].append(block)
                except IOError:
                    print("Something went wrong while reading from {}".format(file_name))
                finally:
                    file.close()
            return True
        except FileNotFoundError:
            return False

    def save_to_file(self, file_name):
        try:
            with open(file_name, "w") as file:
                try:
                    data = "{}\n".format(self.size)
                    data += "{} {}\n{} {}\n".format(self.start.x,
                                                    self.start.y, self.end.x, self.end.y)
                    for row in range(self.size):
                        for col in range(self.size):
                            data += "{} ".format(self.map[row][col])
                        data += "\n"
                    file.write(data)
                except IOError:
                    print("Something went wrong while writing to {}".format(file_name))
                finally:
                    file.close()
            return True
        except:
            return False

    def print_map(self):
        for x in range(0, self.size):
            print(self.map[x])

    def set_start_position(self, x, y):
        if x >= 0 and x < self.size and y >= 0 and y < self.size:
            self.start.x = x
            self.start.y = y

    def set_end_position(self, x, y):
        if x >= 0 and x < self.size and y >= 0 and y < self.size:
            self.end.x = x
            self.end.y = y

    def is_valid(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def is_wall(self, x, y):
        return self.map[x][y] == 1
