import math
import os
import threading
import time
import json

import graphics
from web3 import Web3

import vehicle


# Debug, remove later
COLOR_MAPPING = []
COLOR_MAPPING.append("green")
COLOR_MAPPING.append("blue")
COLOR_MAPPING.append("red")
COLOR_MAPPING.append("coral")
COLOR_MAPPING.append("cyan")
COLOR_MAPPING.append("gold")
COLOR_MAPPING.append("pink")
COLOR_MAPPING.append("brown")
COLOR_MAPPING.append("yellow")
COLOR_MAPPING.append("plum")

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
        self.win = graphics.GraphWin("Grid", win_size_x, win_size_y)
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
        self.vehicle_threads = []

        self.open = True

        # Contract (for coloring)
        url = "http://127.0.0.1:8545"
        address = '0x5B44e05f549988591aDb24ed02d3B8ce16E79d94'
        self.web3 = Web3(Web3.HTTPProvider(url))

        cd_path = os.path.dirname(__file__)
        file_path = os.path.join(cd_path, '..\\..\\..\\RentSpatialNode.json')

        with open(file_path) as f:
            abi = json.load(f)
        self.contract = self.web3.eth.contract(address=address, abi=abi)

        # Color mapping (grid)
        self.color_thread = threading.Thread(target=self.find_colors_from_contract)
        self.color_thread.daemon = True
        self.color_thread.start()

    # Update the colors of the grid if the number of blocks has changed.
    def find_colors_from_contract(self):
        threads = []


        block_count = int(self.web3.eth.blockNumber)
        start_time = 0
        while True:
            # If the number of blocks has not changed, wait a bit.
            if block_count == int(self.web3.eth.blockNumber):
                time.sleep(3)
                continue
            block_count = int(self.web3.eth.blockNumber)

            start_time = time.time()
            color_grid_copy = self.color_grid.copy()

            x = 0
            z = 0 # Not used
            for col in self.grid:
                y = 0
                for rect in col:
                    t = threading.Thread(target=self.update_node, args=(x, y, z, color_grid_copy[x][y], ))
                    t.start()
                    threads.append(t)

                    y += 1
                x += 1

            for t in threads:
                t.join()
            threads.clear()
            self.color_grid = color_grid_copy.copy()

            print('Color update: ',end='')
            print(time.time()-start_time)

    # Changes the color of a rectangle if the owner has changed.
    def update_node(self, x, y, z, cell):
        owner = self.contract.functions.GetOwner(x, y, z).call()
        owner_address = owner[0]
        if int(owner_address, 16) != 0:
            index = self.web3.eth.accounts.index(owner_address)
            color = COLOR_MAPPING[index]
            if not cell.color == color:
                cell.color = COLOR_MAPPING[index]
                cell.changed = True
        elif not cell.color == "white":
            cell.color = "white"
            cell.changed = True

    # Updates the grid coloring and vehicle positions.
    def update(self, dt):

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
            self.vehicles.append(vehicle.GraphicalVehicle(n_vehicles, COLOR_MAPPING[n_vehicles], self.win))

            # Fire up a new instance of the vehicle program.
            cd_path = os.path.dirname(__file__)
            file_path = os.path.join(cd_path, '../../Vehicle/Vehicle/main.py ')

            self.vehicle_threads.append(threading.Thread(target=os.system, args=('cmd /c python ' + file_path + str(n_vehicles),)))
            self.vehicle_threads[len(self.vehicle_threads)-1].daemon = True
            self.vehicle_threads[len(self.vehicle_threads)-1].start()

    # Create a grid of rectangles based on the objects members.
    def init_grid(self):
        rect_size_x = math.floor(self.win_size_x / self.grid_size_x)
        rect_size_y = math.floor(self.win_size_y / self.grid_size_y)

        x = 0
        while x < self.grid_size_x:
            self.grid.insert(x, [])
            self.color_grid.insert(x, [])
            bl_x = x * rect_size_x
            y = 0
            while y < self.grid_size_y:
                bl_y = y * rect_size_y
                rect = graphics.Rectangle(graphics.Point(bl_x, bl_y), graphics.Point(bl_x + rect_size_x, bl_y + rect_size_y))
                self.grid[x].insert(y, rect)
                self.color_grid[x].insert(y, CellColor(x, y, "white"))
                y += 1
            x += 1

    # Initial drawing of the grid.
    def draw_grid(self):
        for col in self.grid:
            for rect in col:
                rect.draw(self.win)

    # Change the color of any changed nodes.
    def color_path(self):
        start_time = time.time()
        x = 0
        for col in self.color_grid:
            y = 0
            for cell in col:
                if cell.changed:
                    self.color_grid[x][y].changed = False
                    self.grid[x][y].setFill(cell.color)
                y = y + 1
            x = x + 1
        #print('Color draw: ',end='')
        #print(time.time()-start_time)
