import graphics
import random
import vehicle
import math
import os
import threading
import time

# Debug, remove later
color_mapping = []
color_mapping.append("green")
color_mapping.append("blue")
color_mapping.append("red")
color_mapping.append("coral")
color_mapping.append("cyan")
color_mapping.append("gold")
color_mapping.append("pink")
color_mapping.append("brown")
color_mapping.append("yellow")
color_mapping.append("plum")

class Simulation:
    def __init__(self, win_size_x, win_size_y, grid_size_x, grid_size_y, frame_rate):
        
        self.win_size_x = win_size_x
        self.win_size_y = win_size_y
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.grid = []

        self.init_grid()
        
        self.cell_size_x = win_size_x / grid_size_x
        self.cell_size_y = win_size_y / grid_size_y
        
        self.win = graphics.GraphWin("Grid", win_size_x, win_size_y, autoflush=False)
        self.win.setCoords(0, 0, win_size_x, win_size_y)
        self.win.setBackground("white")

        self.draw_grid()
        self.vehicles = []

        self.open = True
        
        self.start = None
        self.goal = None      

    def update(self, dt):

        graphics.update(dt**-1)

        if self.win.isClosed():
            self.open = False

        for v in self.vehicles:
            v.update()            
        
        self.color_path()    
    
    # Add a vehicle to the list of vehicles.
    def add_vehicle(self):
        n_vehicles = len(self.vehicles)
        if n_vehicles < 10:

            # Create a new graphical vehicle object and store it in the list.
            self.vehicles.append(vehicle.GraphicalVehicle(n_vehicles, color_mapping[n_vehicles], self.win))

            # Fire up a new instance of the vehicle program.
            threading.Thread(target=os.system, args=('cmd /c python ../../Vehicle/Vehicle/main.py ' + str(n_vehicles),)).start()
            
    
    def init_grid(self):        
        rect_size_x = math.floor(self.win_size_x / self.grid_size_x)
        rect_size_y = math.floor(self.win_size_y / self.grid_size_y)
    
        x = 0
        while x < self.grid_size_x:
            self.grid.insert(x, [])
            bl_x = x * rect_size_x
            y = 0
            while y < self.grid_size_y:
                bl_y = y * rect_size_y
                rect = graphics.Rectangle(graphics.Point(bl_x, bl_y), graphics.Point(bl_x + rect_size_x, bl_y + rect_size_y))
                self.grid[x].insert(y, rect)
                y += 1
            x += 1       
    
    def draw_grid(self):
        for col in self.grid:
            for rect in col:
                rect.draw(self.win)
    
    def color_path(self):
        boi =0        
