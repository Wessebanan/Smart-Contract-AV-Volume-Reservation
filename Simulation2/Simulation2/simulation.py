import graphics
import vehicle
import math
import os
import threading

import json
from web3 import Web3

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

class CellColor:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.changed = False

class Simulation:
    def __init__(self, win_size_x, win_size_y, grid_size_x, grid_size_y):
        
        # Window
        self.win_size_x = win_size_x
        self.win_size_y = win_size_y
        self.win = graphics.GraphWin("Grid", win_size_x, win_size_y, autoflush=False)
        self.win.setCoords(0, 0, win_size_x, win_size_y)
        self.win.setBackground("white")
        
        # Grid
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.grid = []
        self.color_grid = []

        self.init_grid()
        
        self.cell_size_x = win_size_x / grid_size_x
        self.cell_size_y = win_size_y / grid_size_y        

        self.draw_grid()

        # Misc
        self.vehicles = []

        self.open = True   

        # Contract (for coloring)
        url = "http://127.0.0.1:8545"
        address = '0x243b5730647c70796cc6FdeC868bCCA7d199614f'
        self.web3 = Web3(Web3.HTTPProvider(url))

        cd_path = os.path.dirname(__file__)
        file_path = os.path.join(cd_path, 'RentSpatialNode.json')
 
        with open(file_path) as f:
            abi = json.load(f)
        self.contract = self.web3.eth.contract(address=address, abi=abi)

        # Color mapping (grid)
        self.color_thread = threading.Thread(target=self.find_colors_from_contract)
        self.color_thread.start()

    def find_colors_from_contract(self):
        while True:
            x = 0
            z = 0 # Not used
            for col in self.grid:
                y = 0
                for rect in col:
                    owner_address = self.contract.functions.GetOwner(x, y, z).call()
                    if not int(owner_address, 16) == 0:
                        index = self.web3.eth.accounts.index(owner_address)
                        color = color_mapping[index]
                        if not self.color_grid[x][y].color == color:
                            self.color_grid[x][y].color = color_mapping[index]
                            self.color_grid[x][y].changed = True
                    y = y + 1
                x = x + 1
            
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
            self.color_grid.insert(x,[])
            bl_x = x * rect_size_x
            y = 0
            while y < self.grid_size_y:
                bl_y = y * rect_size_y
                rect = graphics.Rectangle(graphics.Point(bl_x, bl_y), graphics.Point(bl_x + rect_size_x, bl_y + rect_size_y))
                self.grid[x].insert(y, rect)
                self.color_grid[x].insert(y, CellColor(x,y,"white"))
                y += 1
            x += 1       
    
    def draw_grid(self):
        for col in self.grid:
            for rect in col:
                rect.draw(self.win)
    
    def color_path(self):
        x = 0
        for col in self.color_grid:
            y = 0
            for cell in col:
                if cell.changed:
                    cell.changed = False
                    self.grid[x][y].setFill(cell.color)
                y = y + 1
            x = x + 1

