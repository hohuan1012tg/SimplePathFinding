import pygame
import queue
import os
import tkinter
from tkinter import messagebox
from tkinter import simpledialog 
import astar
import heuristic
import grid
import search_thread
import search_map

class Color:
    COLOR_DICT = dict(
        BLACK = (0, 0, 0),
        WHITE = (255, 255, 255),
        GREEN = (77, 175, 124),
        LIGHT_GREEN = (200, 247, 197),
        RED = (200, 80, 70),
        BLUE = (64, 150, 211),
        GREY = (110, 110, 110),
        LIGHT_GREY = (180, 180, 180),
        YELLOW = (213, 174, 65),
        LIGHT_YELLOW = (237, 219, 171)
    )

class Window:
    def __init__(self, width=1200, height=600, title="Path Finding Visualization"):
        pygame.init()
        self.text_size_width_area=400
        self.size = [width - self.text_size_width_area, height]
        self.title = title
        self.screen = pygame.display.set_mode([width, height])
        pygame.display.set_caption(title)
        self.screen.fill(Color.COLOR_DICT["LIGHT_GREY"])

    def instructions(self):
        pos_x = self.size[0] + 20
        pos_y = 30
        gap_between_text=20

        myFont = pygame.font.SysFont("Times New Roman", 18)
        textColor = Color.COLOR_DICT["BLACK"]
        instruction = "Enter: Start Searching"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y))
        instruction = "ESC: exit"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text))
        instruction = "Right click on ground and drag to build walls"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*2))
        instruction= "Right click on wall and drag to detroy walls"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*3))
        instruction = "Left click on start and goal to remove them"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*4))
        instruction = "Left click on ground to choose start and goal"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*5))
        instruction = "CTRL + L: clear path"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*6))
        instruction = "CTRL + R: remove map"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*7))
        instruction = "CTRL + O: load map"
        displayText=myFont.render(instruction,True,textColor)
        self.screen.blit(displayText, (pos_x, pos_y+gap_between_text*8))
        instruction = "CTRL + S: save map"
        displayText=myFont.render(instruction,True,textColor)
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
        self.heuristic = heuristic.Heuristic.euclidian_distance
        self.epsilon = 3.0
        self.message_queue = queue.Queue()
        self.time_limited = True
        self.limit = -1

        # Create thread for searching
        if self.prompt_algorithm():
            while self.limit == -1:
                self.limit = self.prompt_time_limit()
            self.search_thread = search_thread.ARAThread(limit=self.limit, epsilon=self.epsilon,message_queue=self.message_queue)
        else:
            self.search_thread = search_thread.AStarThread(heuristic=self.heuristic, message_queue=self.message_queue)
            self.time_limited = False

        # Check whether to add or remove walls
        self.add = True

        # Start point and End point
        self.start = dict( position = search_map.Position(-1, -1), added = False )
        self.end = dict( position = search_map.Position(-1, -1), added = False )

        # Create grid for drawing
        self.gui_grid = grid.Grid(50)
        self.gui_grid.calculate_rect_size(self.window.size[0], self.window.size[1])

    def load_map(self, map):
        startx, starty, endx, endy, self.search_thread.map = self.gui_grid.load_map(map)
        self.gui_grid.calculate_rect_size(self.window.size[0], self.window.size[1])

        self.start = dict( position = search_map.Position(startx, starty), added = True )
        self.end = dict( position = search_map.Position(endx, endy), added = True )

    def load_map_from_file(self):
        tkinter.Tk().wm_withdraw()
        filename = simpledialog.askstring("Enter file name", "Open map from: ")
        if filename == None:
            return
        map = search_map.Map()
        if map.read_from_file(filename):
            self.prompt_message("Map loaded successfully", "INFO")
            self.load_map(map)
        else:
            self.prompt_message("Error loading map\nMake sure the file exists", "ERROR")
    
    def save_map(self):
        if not self.start["added"] or not self.end["added"]:
            return None
        saved = self.gui_grid.save_map()
        start = self.start["position"]
        end = self.end["position"]
        saved.set_start_position(start.x, start.y)
        saved.set_end_position(end.x, end.y)
        self.search_thread.map = saved 
        return saved
    
    def save_map_to_file(self):
        result = self.save_map()
        if result != None:
            self.prompt_message("Map saved successfully")
            tkinter.Tk().wm_withdraw()
            ok = messagebox.askyesno("Save to File", "Do you want to save to file ?")
            if ok:
                tkinter.Tk().wm_withdraw()
                filename = simpledialog.askstring("Enter file name", "Save map to:")
                if filename == None:
                    return
                if result.save_to_file(filename):
                    self.prompt_message("Successfully saved to file", "INFO")
                else:
                    self.prompt_message("Error saving to file\nSomething went wrong", "ERROR")
        else:
            self.prompt_message("Error saving map", "ERROR")
    
    def prepare_thread(self):
        if self.time_limited:
            self.search_thread = search_thread.ARAThread(limit=self.limit, epsilon=self.epsilon, message_queue=self.message_queue, heuristic=self.heuristic)
        else:
            self.search_thread = search_thread.AStarThread(heuristic=self.heuristic, message_queue=self.message_queue)
    
    def prompt_exit(self):
        tkinter.Tk().wm_withdraw()
        answer = messagebox.askyesno("Exit", "Do you want to exit")
        if answer:
            self.is_done = True

    def prompt_algorithm(self):
        tkinter.Tk().wm_withdraw()
        answer = messagebox.askyesno("A* or ARA*", "Run with time limited ?")
        return answer

    def prompt_heuristic(self):
        tkinter.Tk().wm_withdraw()
        msg = "EUCLIDIAN - Euclidian distance\n"
        msg += "MAX DX DY - Maximum of dx and dy\n"
        msg += "MIN DX DY - Minimum of dx and dy\n"
        msg += "Your choice:"
        chosen_heuristic = simpledialog.askstring("Heuristic", msg).upper()
        thread_heuristic = None
        if chosen_heuristic == "EUCLIDIAN":
            thread_heuristic = heuristic.Heuristic.euclidian_distance
        elif chosen_heuristic == "MAX DX DY":
            thread_heuristic = heuristic.Heuristic.max_dx_dy
        elif chosen_heuristic == "MIN DX DY":
            thread_heuristic = heuristic.Heuristic.min_dx_dy
        else:
            self.prompt_message("Unknown heuristic function, use Euclidian distance as default", "ERROR")
            thread_heuristic = heuristic.Heuristic.euclidian_distance
        
        self.heuristic = thread_heuristic
        self.search_thread.heuristic = thread_heuristic

    def prompt_epsilon(self):
        tkinter.Tk().wm_withdraw()
        epsilon_str = simpledialog.askstring("Epsilon", "Set epsilon to:")
        try:
            epsilon = float(epsilon_str)
            if epsilon >= 1.0:
                self.search_thread.epsilon = epsilon
            else:
                raise ValueError
            self.epsilon = epsilon
        except:
            self.prompt_message("Epsilon must be number and at least 1.0, use 1.0 as default", "ERROR")
            self.epsilon = 1.0
        finally:
            self.search_thread.epsilon = epsilon
        
    def prompt_time_limit(self):
        tkinter.Tk().wm_withdraw()
        limit = simpledialog.askstring("Time limit", "Limit time to (ms):")
        try:
            limit_as_number = float(limit)
            if limit_as_number <= 0:
                raise ValueError
            return limit_as_number
        except:
            self.prompt_message("Please enter a positive number", "ERROR")  
            return -1
    
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
                if not self.gui_grid.is_valid_position(row, column):
                    return
                if self.gui_grid.get_grid_value(row, column) == grid.Grid.NO_WALL_ID:
                    self.add = True
                else:
                    self.add = False
                if event.button == 3:
                    self.modify_start_end(row, column)
    
    def get_item_at_mouse_position(self):
        pos = pygame.mouse.get_pos()
        column = int(pos[0] // (self.gui_grid.rect_size[0] + self.gui_grid.margin))
        row = int(pos[1] // (self.gui_grid.rect_size[1] + self.gui_grid.margin))
        return row, column
                
    def choose_start_end(self, x, y):
        if not self.start["added"]:
            self.start["position"] = search_map.Position(x, y)
            self.start["added"] = True
            self.gui_grid.push_grid_value(self.start["position"].x, self.start["position"].y, grid.Grid.START_END_ID)
        elif not self.end["added"]:
            self.end["position"] = search_map.Position(x, y)
            self.end["added"] = True
            self.gui_grid.push_grid_value(self.end["position"].x, self.end["position"].y, grid.Grid.START_END_ID)
        else:
            self.prompt_message("Start and Goal already chosen", "WARNING")
    
    def remove_start_end(self, x, y):
        pos = search_map.Position(x, y)
        if self.start["position"] != pos and self.end["position"] != pos:
            return False

        if self.start["added"] and self.end["added"]:
            # If start is clicked, swap it's position with end
            if self.start["position"] == pos:
                self.end["position"], self.start["position"] = self.start["position"], self.end["position"]
            # Remove end
            self.gui_grid.pop_grid_value(self.end["position"].x, self.end["position"].y, grid.Grid.START_END_ID)
            self.end["position"] = search_map.Position(-1, -1)
            self.end["added"] = False
        elif self.start["added"]:
            self.gui_grid.pop_grid_value(self.start["position"].x, self.start["position"].y, grid.Grid.START_END_ID)
            self.start["position"] = search_map.Position(-1, -1)
            self.start["added"] = False

    def modify_wall(self, x, y):
        if not self.gui_grid.is_valid_position(x, y):
            return
        position = search_map.Position(x, y)
        if position == self.start["position"] or position == self.end["position"]:
            return

        if self.add:
            self.gui_grid.push_grid_value(x, y, grid.Grid.WALL_ID)
        else:
            self.gui_grid.pop_grid_value(x, y, grid.Grid.WALL_ID)

    def modify_start_end(self, x, y):
        if not self.gui_grid.is_valid_position(x, y):
            return
        if self.add:
            self.choose_start_end(x, y)
        else:
            self.remove_start_end(x, y)

    def handle_input(self):
        if self.input_lock:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] and keys[pygame.K_h]:
            self.prompt_heuristic()
        if keys[pygame.K_LCTRL] and keys[pygame.K_e]:
            self.prompt_epsilon()
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
        time_got = pygame.time.get_ticks()
        elapsed_time = time_got - self.current_time
        if self.time_limited and elapsed_time < 5:
            return
        if not self.time_limited and elapsed_time < 5:
            return
       
        self.current_time = time_got
        if not self.message_queue.empty():
            message = self.message_queue.get_nowait()
            action = message.action
            if action == "LOCK":
                self.input_lock = True
            elif action == "UNLOCK":
                self.input_lock = False
                if self.time_limited:
                    return
                msg = "Searching finished in {} ms\n".format(astar.AStar.search_map.time_elapsed)
                if message.param:
                    msg += "Path length is {}".format(len(self.search_thread.result[1]))
                else:
                    msg += "Path not found"
                self.prompt_message(msg, "INFO")
            elif action == "ARA_UNLOCK":
                if self.time_limited:
                    msg = "Searching finished in {} ms\n".format(self.search_thread.result[0])
                    if self.search_thread.result[2]:
                        msg += "Limit satistifed\n"
                    else:
                        msg += "Limit not satisfied\n"
                    msg += "Epsilon: {}".format(self.search_thread.result[1])
                    self.prompt_message(msg, "INFO")
            elif action == "POP":
                self.gui_grid.pop_grid_value(message.x, message.y, message.param)
            elif action == "PUSH":
                self.gui_grid.push_grid_value(message.x, message.y, message.param)
            elif action == "CLEAR":
                self.clear_path()
            elif action == "ARA_INFO":
                if self.time_limited:
                    msg = "Searching finished in {} ms\n".format(message.param[2])
                    msg += "Path length: {}\n".format(message.param[1])
                    msg += "Epsilon: {}".format(message.param[0])
                    self.prompt_message(msg, "INFO")

    def clear_start_end(self):
        if self.start["added"]:
            self.gui_grid.push_grid_value(self.start["position"].x, self.start["position"].y, grid.Grid.NO_WALL_ID)
            self.start["position"] = search_map.Position(-1, -1)
            self.start["added"] = False
        if self.end["added"]:
            self.gui_grid.push_grid_value(self.end["position"].x, self.end["position"].y, grid.Grid.NO_WALL_ID)
            self.end["position"] = search_map.Position(-1, -1)
            self.end["added"] = False

    def clear_path(self):
        for row in range(self.gui_grid.row_num):
            for col in range(self.gui_grid.col_num):
                self.gui_grid.pop_grid_value(row, col, grid.Grid.POP_ID)
                self.gui_grid.pop_grid_value(row, col, grid.Grid.IN_QUEUE_ID)
                self.gui_grid.pop_grid_value(row, col, grid.Grid.CORRECT_PATH_ID)
    
    def clear_walls(self):
        for row in range(self.gui_grid.row_num):
            for col in range(self.gui_grid.col_num):
                self.gui_grid.pop_grid_value(row, col, grid.Grid.WALL_ID)
    
    def clear_all(self):
        self.clear_path()
        self.clear_start_end()
        self.clear_walls()

    def render(self):
        self.window.screen.fill(Color.COLOR_DICT["LIGHT_GREY"])
        self.window.instructions()
        for row in range(self.gui_grid.row_num):
            for col in range(self.gui_grid.col_num):
                grid_item_value = self.gui_grid.grid_items[row][col].top()
                color = Color.COLOR_DICT["WHITE"]
                if grid_item_value == grid.Grid.START_END_ID or grid_item_value == grid.Grid.CORRECT_PATH_ID:
                    color = Color.COLOR_DICT["RED"]
                elif grid_item_value == grid.Grid.WALL_ID:
                    color = Color.COLOR_DICT["GREY"]
                elif grid_item_value == grid.Grid.POP_ID:
                    color = Color.COLOR_DICT["YELLOW"]
                elif grid_item_value == grid.Grid.IN_QUEUE_ID:
                    color = Color.COLOR_DICT["LIGHT_GREEN"]

                pygame.draw.rect(self.window.screen, color, [
                    (self.gui_grid.rect_size[0] + self.gui_grid.margin) * col + self.gui_grid.margin,
                    (self.gui_grid.rect_size[1] + self.gui_grid.margin) * row + self.gui_grid.margin,
                    self.gui_grid.rect_size[0],
                    self.gui_grid.rect_size[1]
                ])
        self.window.display()

    def run(self):
        while not self.is_done:
            self.handle_event()
            self.handle_input()
            self.handle_message()
            self.render()
            #self.clock.tick(20)
        pygame.quit()
        if self.search_thread.started:
            self.search_thread.join()

if __name__ == "__main__":
    app = Application()
    map = search_map.Map()
    map.read_from_file("input.txt")

    app.run()