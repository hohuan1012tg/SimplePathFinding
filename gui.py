import pygame
import copy
import sys
import os
import queue
import tkinter
import astar
from tkinter import messagebox
from tkinter import simpledialog 
from math import sqrt
from timeit import timeit

# Create grid 
# Create empty list
class Ultilities:
    @staticmethod
    def init_pygame():
        os.environ["SDL_VIDEO_WINDOW_POS"] = "50,50"
        pygame.init()

    @staticmethod
    def create_grid(row_num, col_num, default_value):
        grid = []
        for row in range(0, row_num):
            a_row = []
            for col in range(0, col_num):
                item = GridItem()
                item.push(default_value)
                a_row.append(item)
            grid.append(a_row)
        return grid
    
    @staticmethod
    def create_map(size, default_value):
        matrix = []
        for row in range(size):
            a_row = []
            for col in range(size):
                a_row.append(default_value)
            matrix.append(a_row)
        map = astar.Map()
        map.map = matrix
        map.size = size
        return map

class Message:
    def __init__(self, x=0, y=0, action=None, param=None):
        self.x = x
        self.y = y
        self.action = action
        self.param = param

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
        self.grid = Ultilities.create_grid(size, size, Grid.NO_WALL_ID) 
        self.row_num = size 
        self.col_num = size 
        self.rect_size = [20, 20]
        self.margin = 1
        self.map = Ultilities.create_map(size, 0)

    def load_map(self, map):
        self.map = map
        self.row_num = map.size
        self.col_num = map.size 
        self.grid = Ultilities.create_grid(self.row_num, self.col_num, Grid.NO_WALL_ID)
        for row in range(self.row_num):
            for col in range(self.col_num):
                if map.map[row][col] == 1:
                    self.grid[row][col].push(Grid.WALL_ID)
        self.pop_grid_value(map.start.x, map.start.y, Grid.WALL_ID)
        self.push_grid_value(map.start.x, map.start.y, Grid.START_END_ID)

        self.pop_grid_value(map.end.x, map.end.y, Grid.WALL_ID)
        self.push_grid_value(map.end.x, map.end.y, Grid.START_END_ID)

        return map.start.x, map.start.y, map.end.x, map.end.y
    
    def save_map(self):
        # Map size and grid size not matched
        # Create new map
        if self.map.size != self.row_num:
            self.map = Ultilities.create_map(self.row_num, 0)
        for row in range(self.row_num):
            for col in range(self.col_num):
                value = self.get_grid_value(row, col)
                if value == Grid.NO_WALL_ID:
                    self.map.map[row][col] = 0
                elif value == Grid.WALL_ID:
                    self.map.map[row][col] = 1
    
    def calculate_rect_size(self, screen_width, screen_height):
        self.rect_size[0] = (screen_width - self.margin * (self.col_num + 1)) / self.col_num
        self.rect_size[1] = (screen_height - self.margin * (self.row_num + 1)) / self.row_num

    def push_grid_value(self, x, y, value):
        self.grid[x][y].push(value)
    
    def pop_grid_value(self, x, y, value):
        self.grid[x][y].pop(value)
    
    def get_grid_value(self, x, y):
        return self.grid[x][y].top()

    def get_grid_item(self, x, y):
        return self.grid[x][y]

    def is_valid_position(self, x, y):
        if x < 0 or x >= self.row_num or y < 0 or y >= self.col_num:
            return False
        return True

class Color:
    COLOR_DICT = dict(
    	aliceblue_background= (240,248,255),
    	gray_wall= (128,128,128),
    	brown_correctpath=(139,105,105),
        BLACK = (0, 0, 0),
        WHITE = (255, 255, 255),
        lightcyan2_passed = (209,238,238),
        green_opened = (173,255,47),
        RED = (244, 101, 40)
    )

class Window:
    def __init__(self, width=1200, height=600, title="Pygame Application"):
        self.text_size_width_area=400 
        self.size = [width - self.text_size_width_area, height]
        self.title = title
        self.screen = pygame.display.set_mode([width,height])
        pygame.display.set_caption(title)
        self.screen.fill(Color.COLOR_DICT["aliceblue_background"])
        #self.instructions()
        
    def instructions(self):
        pos_x = self.size[0] + 20
        pos_y = 30
        gap_between_text=20

        myFont = pygame.font.SysFont("Times New Roman", 18)
        instruction = "Enter: Start Searching"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y))
        instruction = "ESC: exit"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text))
        instruction = "Right click on ground and drag to build walls"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*2))
        instruction= "Right click on wall and drag to detroy walls"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*3))
        instruction = "Left click on start and goal to remove them"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*4))
        instruction = "Left click on ground to choose start and goal"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*5))
        instruction = "CTRL + L: clear path"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*6))
        instruction = "CTRL + R: remove map"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*7))
        instruction = "CTRL + O: load map"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*8))
        instruction = "CTRL + S: save map"
        displayText=myFont.render(instruction,True,Color.COLOR_DICT["RED"])
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*9))
        
    def display(self):
        pygame.display.flip()

class Application:
    def __init__(self):
        self.window = Window()
        self.is_done = False
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.input_lock = False
        self.FPS = 60

        self.message_queue = queue.Queue()
        self.search_thread = astar.SearchThread(message_queue=self.message_queue)
        # Set key repeat interval
        pygame.key.set_repeat(100, 100)
        self.add = True

        self.start = dict( position = astar.Position(-1, -1), added = False )
        self.end = dict( position = astar.Position(-1, -1), added = False )

        self.grid = Grid(30)
        self.grid.calculate_rect_size(self.window.size[0], self.window.size[1])

        #self.prompt_instruction()

    def load_map(self, map):
        startx, starty, endx, endy = self.grid.load_map(map)
        self.search_thread.map = self.grid.map
        self.grid.calculate_rect_size(self.window.size[0], self.window.size[1])

        self.start = dict( position = astar.Position(startx, starty), added = True )
        self.end = dict( position = astar.Position(endx, endy), added = True )

    def load_map_from_file(self):
        tkinter.Tk().wm_withdraw()
        filename = simpledialog.askstring("Enter file name", "Open map from: ")
        map = astar.Map()
        if map.read_from_file(filename):
            self.prompt_message("Map loaded successfully", "INFO")
            self.load_map(map)
        else:
            self.prompt_message("Error loading map\nMake sure the file exists", "ERROR")
    
    def save_map(self):
        if not self.start["added"] or not self.end["added"]:
            return False
        self.grid.save_map()
        start = self.start["position"]
        end = self.end["position"]
        self.grid.map.set_start_position(start.x, start.y)
        self.grid.map.set_end_position(end.x, end.y)
        self.search_thread.map = self.grid.map
        return True
    
    def save_map_to_file(self):
        result = self.save_map()
        if result:
            self.prompt_message("Map saved successfully","INFO")
            tkinter.Tk().wm_withdraw()
            ok = messagebox.askyesno("Save to File", "Do you want to save to file ?")
            if ok:
                tkinter.Tk().wm_withdraw()
                filename = simpledialog.askstring("Enter file name", "Save map to:")
                if self.grid.map.save_to_file(filename):
                    self.prompt_message("Successfully saved to file", "INFO")
                else:
                    self.prompt_message("Error saving to file\nSomething went wrong", "ERROR")
        else:
            self.prompt_message("Error saving map", "ERROR")
    
    def prepare_thread(self):
        self.search_thread = astar.SearchThread(message_queue=self.message_queue)
    
    def prompt_exit(self):
        tkinter.Tk().wm_withdraw()
        answer = messagebox.askyesno("Exit", "Do you want to exit")
        if answer:
            self.is_done = True
    
    def prompt_instruction(self):
        tkinter.Tk().wm_withdraw()
        instruction = "Press Enter to save map\n"
        instruction += "Right click on ground and drag to build walls\n"
        instruction += "Right click on wall and drag to detroy walls\n"
        instruction += "Left click on start and goal to remove them\n"
        instruction += "Left click on ground to choose start and goal\n"
        messagebox.showinfo("Instruction", instruction)
    
    def prompt_message(self, message, mode="INFO"):
        tkinter.Tk().wm_withdraw()
        if mode == "INFO":
            messagebox.showinfo("Info", message)
        elif mode == "ERROR":
            messagebox.showerror("Error", message)
        elif mode == "WARNING":
            messagebox.showwarning("Warning", message)

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.prompt_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.prompt_exit()
                if not self.input_lock:
                    if event.key == pygame.K_RETURN:
                        if self.search_thread.finished:
                            self.prepare_thread()
                            self.clear_path()
                        self.save_map()
                        self.search_thread.start()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.input_lock:
                row, column = self.get_item_at_mouse_position()
                if column != -1:
                    if self.grid.get_grid_value(row, column) == Grid.NO_WALL_ID:
                        self.add = True
                    else:
                        self.add = False
                    if event.button == 3:
                        self.modify_start_end(row, column)
    
    def get_item_at_mouse_position(self):
        pos = pygame.mouse.get_pos()
        if pos[0] < self.window.size[0]: 
            column = int(pos[0]// (self.grid.rect_size[0] + self.grid.margin))
            row = int(pos[1] // (self.grid.rect_size[1] + self.grid.margin))
        else:
            row=column=-1
        return row, column

                
    def choose_start_end(self, x, y):
        if not self.start["added"]:
            self.start["position"] = astar.Position(x, y)
            self.start["added"] = True
            self.grid.push_grid_value(self.start["position"].x, self.start["position"].y, Grid.START_END_ID)
        elif not self.end["added"]:
            self.end["position"] = astar.Position(x, y)
            self.end["added"] = True
            self.grid.push_grid_value(self.end["position"].x, self.end["position"].y, Grid.START_END_ID)
        else:
            self.prompt_message("Start and Goal already chosen", "WARNING")
    
    def remove_start_end(self, x, y):
        pos = astar.Position(x, y)
        if self.start["position"] != pos and self.end["position"] != pos:
            return False

        if self.start["added"] and self.end["added"]:
            # If start is clicked, swap it's position with end
            if self.start["position"] == pos:
                self.end["position"], self.start["position"] = self.start["position"], self.end["position"]
            # Remove end
            self.grid.pop_grid_value(self.end["position"].x, self.end["position"].y, Grid.START_END_ID)
            self.end["position"] = astar.Position(-1, -1)
            self.end["added"] = False
        elif self.start["added"]:
            self.grid.pop_grid_value(self.start["position"].x, self.start["position"].y, Grid.START_END_ID)
            self.start["position"] = astar.Position(-1, -1)
            self.start["added"] = False

    def modify_wall(self, x, y):
        if not self.grid.is_valid_position(x, y) or self.grid.get_grid_value(x,y) == Grid.START_END_ID:
            return
        if self.add:
            self.grid.push_grid_value(x, y, Grid.WALL_ID)
        else:
            self.grid.pop_grid_value(x, y, Grid.WALL_ID)

    def modify_start_end(self, x, y):
        if not self.grid.is_valid_position(x, y):
            return
        if self.add:
            self.choose_start_end(x, y)
        else:
            self.remove_start_end(x, y)

    def handle_input(self):
        if self.input_lock:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] and keys[pygame.K_l]:
            self.clear_path()
        if keys[pygame.K_LCTRL] and keys[pygame.K_r]:
            self.clear_all()
        if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
            self.save_map_to_file()
        if keys[pygame.K_LCTRL] and keys[pygame.K_o]:
            self.load_map_from_file()

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.modify_wall(*self.get_item_at_mouse_position())

    def handle_message(self):
        if not self.message_queue.empty():
            message = self.message_queue.get_nowait()
            action = message.action
            if action == "LOCK":
                self.input_lock = True
            elif action == "UNLOCK":
                self.input_lock = False
                msg = "Searching finished in {} ms\n".format(astar.PathFinding.search_map.time_elapsed)
                if message.param:
                    msg += "Path length is {}".format(len(self.search_thread.result[1]))
                else:
                    msg += "Path not found"
                self.prompt_message(msg, "INFO")
            elif action == "POP" and self.grid.get_grid_value(message.x,message.y)!= Grid.START_END_ID:
                self.grid.pop_grid_value(message.x, message.y, message.param)
            elif action == "PUSH" and self.grid.get_grid_value(message.x,message.y)!= Grid.START_END_ID:
                self.grid.push_grid_value(message.x, message.y, message.param)
    
    def clear_start_end(self):
        if self.start["added"]:
            self.grid.push_grid_value(self.start["position"].x, self.start["position"].y, Grid.NO_WALL_ID)
            self.start["position"] = astar.Position(-1, -1)
            self.start["added"] = False
        if self.end["added"]:
            self.grid.push_grid_value(self.end["position"].x, self.end["position"].y, Grid.NO_WALL_ID)
            self.end["position"] = astar.Position(-1, -1)
            self.end["added"] = False

    def clear_path(self):
        for row in range(self.grid.row_num):
            for col in range(self.grid.col_num):
                self.grid.pop_grid_value(row, col, Grid.POP_ID)
                self.grid.pop_grid_value(row, col, Grid.IN_QUEUE_ID)
                self.grid.pop_grid_value(row, col, Grid.CORRECT_PATH_ID)
    
    def clear_walls(self):
        for row in range(self.grid.row_num):
            for col in range(self.grid.col_num):
                self.grid.pop_grid_value(row, col, Grid.WALL_ID)
    
    def clear_all(self):
        self.clear_path()
        self.clear_start_end()
        self.clear_walls()

    def render(self):
        self.window.screen.fill(Color.COLOR_DICT["aliceblue_background"])
        self.window.instructions()
        for row in range(self.grid.row_num):
            for col in range(self.grid.col_num):
                grid_item_value = self.grid.grid[row][col].top()
                color = Color.COLOR_DICT["WHITE"]
                if grid_item_value == Grid.START_END_ID:
                    color = Color.COLOR_DICT["RED"]
                elif grid_item_value == Grid.CORRECT_PATH_ID:
                	color = Color.COLOR_DICT["brown_correctpath"]
                elif grid_item_value == Grid.WALL_ID:
                    color = Color.COLOR_DICT["gray_wall"]
                elif grid_item_value == Grid.POP_ID:
                    color = Color.COLOR_DICT["lightcyan2_passed"]
                elif grid_item_value == Grid.IN_QUEUE_ID:
                    color = Color.COLOR_DICT["green_opened"]

                pygame.draw.rect(self.window.screen, color, [
                    (self.grid.rect_size[0] + self.grid.margin) * col + self.grid.margin,
                    (self.grid.rect_size[1] + self.grid.margin) * row + self.grid.margin,
                    self.grid.rect_size[0],
                    self.grid.rect_size[1]
                ])
        self.window.display()

    def run(self):
        while not self.is_done:
            self.handle_event()
            self.handle_input()
            self.handle_message()
            self.render()
            self.clock.tick(self.FPS)
        pygame.quit()
        if self.search_thread.started:
            self.search_thread.join()

if __name__ == "__main__":
    Ultilities.init_pygame()
    app = Application()
    map = astar.Map()

    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        map.read_from_file(input_path)
        app.load_map(map)

    
    app.run()
    #app.save_to_file()