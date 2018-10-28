import utilities

class GridItem:
    def __init__(self):
        self.stack = []
    
    def push(self, value):
        self.stack.append(value)
    
    def top(self):
        return self.stack[-1]

    def pop(self, value):
        self.stack = list(filter(lambda a: a != value, self.stack))
    
    def empty(self):
        return len(self.stack) == 0

class Grid:
    NO_WALL_ID = 0
    WALL_ID = 1
    START_END_ID = 2
    IN_QUEUE_ID = 3
    POP_ID = 4
    CORRECT_PATH_ID = 5

    def __init__(self, size):
        self.grid_items = utilities.Utilities.create_grid(size, size, Grid.NO_WALL_ID) 
        self.row_num = size 
        self.col_num = size 
        self.rect_size = [20, 20]
        self.margin = 1

    def load_map(self, map):
        self.row_num = map.size
        self.col_num = map.size 
        self.grid_items = utilities.Utilities.create_grid(self.row_num, self.col_num, Grid.NO_WALL_ID)
        for row in range(self.row_num):
            for col in range(self.col_num):
                if map.map[row][col] == 1:
                    self.grid_items[row][col].push(Grid.WALL_ID)
        self.pop_grid_value(map.start.x, map.start.y, Grid.WALL_ID)
        self.push_grid_value(map.start.x, map.start.y, Grid.START_END_ID)

        self.pop_grid_value(map.end.x, map.end.y, Grid.WALL_ID)
        self.push_grid_value(map.end.x, map.end.y, Grid.START_END_ID)

        return map.start.x, map.start.y, map.end.x, map.end.y, map
    
    def save_map(self):
        # Map size and grid size not matched
        # Create new map
        map = utilities.Utilities.create_map(self.row_num, 0)
        for row in range(self.row_num):
            for col in range(self.col_num):
                value = self.get_grid_value(row, col)
                if value == Grid.NO_WALL_ID:
                    map.map[row][col] = 0
                elif value == Grid.WALL_ID:
                    map.map[row][col] = 1
        return map
    
    def calculate_rect_size(self, screen_width, screen_height):
        self.rect_size[0] = (screen_width - self.margin * (self.col_num + 1)) / self.col_num
        self.rect_size[1] = (screen_height - self.margin * (self.row_num + 1)) / self.row_num

    def push_grid_value(self, x, y, value):
        self.grid_items[x][y].push(value)
    
    def pop_grid_value(self, x, y, value):
        self.grid_items[x][y].pop(value)
    
    def get_grid_value(self, x, y):
        return self.grid_items[x][y].top()

    def get_grid_item(self, x, y):
        return self.grid_items[x][y]

    def is_valid_position(self, x, y):
        if x < 0 or x >= self.row_num or y < 0 or y >= self.col_num:
            return False
        return True