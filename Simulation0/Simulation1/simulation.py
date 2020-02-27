import graphics
import vehicle
import math
import threading
import random

class GraphicalVehicle:
    def __init__(self, p_vehicle, color, win):
        self.win = win
        
        self.circle = graphics.Circle(graphics.Point(p_vehicle.pos.x, p_vehicle.pos.y), p_vehicle.dimensions.x)
        self.circle.setWidth(5)
        self.circle.setFill(color)
        #self.circle.draw(self.win)        
        self.drawn = False

        self.color = color
        self.vehicle = p_vehicle

    def update(self, dt):
        self.vehicle.update(dt)
        if self.vehicle.done and self.drawn:
            self.circle.undraw()
            self.circle.drawn = False
        elif not self.drawn and not self.vehicle.done:
            self.circle.draw(self.win)
            self.drawn = True
        else:
            self.circle.move(self.vehicle.pos.x - self.circle.getCenter().getX(), self.vehicle.pos.y - self.circle.getCenter().getY())

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
        self.paths = []

        self.open = True
        
        self.start = None
        self.goal = None

    def update(self, dt):

        graphics.update(dt**-1)

        if self.win.isClosed():
            self.open = False

        for v in self.vehicles:
            v.update(dt)            
        
        self.color_path()

        click = self.win.checkMouse()
        if click and not self.start:
            self.start = click
        elif click:
            self.goal = click
            self.add_vehicle(self.start.x, self.start.y, graphics.color_rgb(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            self.set_goal_for_vehicle(len(self.vehicles)-1, self.goal.x, self.goal.y)
            self.start = None
            self.goal = None
    
    
    # Add a vehicle to the list of vehicles.
    def add_vehicle(self, pos_x, pos_y, color):
        if len(self.vehicles) < 10:
            self.vehicles.append(GraphicalVehicle(vehicle.Vehicle(pos_x, pos_y, len(self.vehicles), self.cell_size_x, self.cell_size_y), color, self.win))
    
    def set_goal_for_vehicle(self, index, pos_x, pos_y):
        path = self.vehicles[index].vehicle.create_path(pos_x, pos_y)
        self.paths.insert(index, path.copy())
    
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
        # Redraw path if length has changed.
        for v in self.vehicles:
            if v.vehicle.rent_thread.is_alive():
                continue
            if len(self.paths[self.vehicles.index(v)]) != len(v.vehicle.rented_path):
                for cell in self.paths[self.vehicles.index(v)]:
                    self.grid[math.floor(cell.x)][math.floor(cell.y)].setFill("white")
                self.paths[self.vehicles.index(v)] = v.vehicle.rented_path
            for cell in v.vehicle.rented_path:
                self.grid[math.floor(cell.x)][math.floor(cell.y)].setFill(v.color)
    
    