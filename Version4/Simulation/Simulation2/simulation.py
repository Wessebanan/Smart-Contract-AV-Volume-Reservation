import math
import os
import threading
import time
import json
import subprocess

import graphics
from web3 import Web3
from web3.middleware import geth_poa_middleware

import vehicle


# Debug, remove later
colors = []
colors.append("green")
colors.append("blue")
colors.append("red")
colors.append("coral")
colors.append("cyan")
colors.append("gold")
colors.append("pink")
colors.append("brown")
colors.append("yellow")
colors.append("plum")

cd = os.path.dirname(__file__)
account_list_path = os.path.join(cd, '../../../network/info/account_list.txt')

color_mapping = {}

with open(account_list_path) as account_list:
    contents = account_list.readlines()
    for i in range(0, int(len(contents) / 2)):
        color_mapping[contents[i*2].rstrip('\n')] = colors[i]

RENT_NODE_INPUT = 7
CHANGE_OWNER_INPUT = 6

class CellColor:
    def __init__(self, x, y, color, end_time):
        self.x = x
        self.y = y
        self.color = color
        self.end_time = end_time
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

        # Contract (for coloring). Connecting to the first sealer node to not disturb vehicle nodes.
        self.port = 8551

        # Setup connection to smart contract at @param address with locally stored abi.
        url = "http://127.0.0.1:" + str(self.port)
        self.web3 = Web3(Web3.HTTPProvider(url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]

        cd_path = os.path.dirname(__file__)
        json_path = os.path.join(cd_path, '../../../network/info/RentSpatialNode.json')
        contract_address_path = os.path.join(cd_path, '../../../network/info/contractAddress.txt')

        # Fetch contract info from files.
        with open(contract_address_path) as f:
            address = f.readline()
            
        with open(json_path) as f:
            json_file   = json.load(f)
            abi         = json_file['abi']
            bytecode    = json_file['bytecode']

        # Build contract from info.
        self.contract = self.web3.eth.contract(address=address, abi=abi, bytecode=bytecode)

        self.current_block = int(self.web3.eth.blockNumber)

    # Updates the grid coloring and vehicle positions.
    def update(self, dt):

        if self.win.isClosed():
            self.open = False

        for v in self.vehicles:
            v.update()

        self.color_path()

    # Add a vehicle to the list of vehicles.
    def add_vehicle(self, mode, amount):
        n_vehicles = len(self.vehicles)
        if n_vehicles < 10:

            # Create a new graphical vehicle object and store it in the list.
            self.vehicles.append(vehicle.GraphicalVehicle(n_vehicles, colors[n_vehicles], self.win))

            # Fire up a new instance of the vehicle program.
            cd_path = os.path.dirname(__file__)
            file_path = os.path.join(cd_path, '..\\..\\Vehicle\\Vehicle\\main.py ')

            #p = subprocess.Popen('start '+ file_path + str(n_vehicles), shell=True)
            #self.vehicle_threads.append(p)
            
            t = threading.Thread(target=os.system, args=('cmd /c python3 ' + file_path + str(n_vehicles) + ' ' + str(mode) + ' ' + str(amount),))
            t.daemon = True
            t.start()
            self.vehicle_threads.append(t)



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
                self.color_grid[x].insert(y, CellColor(x, y, "white", 0))
                y += 1
            x += 1

    # Initial drawing of the grid.
    def draw_grid(self):
        for col in self.grid:
            for rect in col:
                rect.draw(self.win)

    # Change the color of any changed nodes.
    def color_path(self):

        # Check contract for changes.
        if not self.current_block == int(self.web3.eth.blockNumber):
            block = self.web3.eth.getBlock('latest')
            self.current_block = int(self.web3.eth.blockNumber)
            # If the block is not empty, check the transactions for changes.
            if not len(block.transactions) == 0:
                for tx in block.transactions:                   
                    tx_info = self.web3.eth.getTransaction(tx)
                    tx_receipt = self.web3.eth.getTransactionReceipt(tx_info.hash)
                    
                    # See if the transaction succeeded.
                    hexresult = tx_receipt['logs'][0]['data']
                    success = bool(int(hexresult,16))
                    
                    if success:
                        # Get the coordinates and owner from the tx information.
                        tx_input = self.contract.decode_function_input(tx_info['input'])[1]
                        x = tx_input['_x']
                        y = tx_input['_y']
                        z = tx_input['_z']

                        # Getting owner and end time based on if regular rental or owner change.
                        owner = ''
                        end_time = 0

                        if len(tx_input) == 7: # Rent Node.
                            start = tx_input['_start']
                            duration = tx_input['_duration']            
                            if start < block.timestamp:
                                start = block.timestamp

                            end_time = start + duration
                            owner = tx_info['from']

                        else:
                            end_time = self.contract.functions.GetEndTime(x, y, z).call() # Add Time and Change Owner.
                            if len(tx_input) == 6: # Change Owner.
                                owner = tx_input['_newOwner']

                        # Update end time of cell rental.
                        self.color_grid[x][y].end_time = end_time

                        if not owner == '':
                            # Update the color of the cell.                                             
                            color = color_mapping[owner]
                            self.color_grid[x][y].color = color
                            self.color_grid[x][y].changed = True

        # Change colors of cells where necessary.
        x = 0
        for col in self.color_grid:
            y = 0
            for cell in col:
                if not cell.color == "white":
                    if time.time() > cell.end_time:
                        self.color_grid[x][y].color = "white"
                        self.color_grid[x][y].changed = True
                        self.color_grid[x][y].end_time = 0

                if cell.changed:
                    self.color_grid[x][y].changed = False
                    self.grid[x][y].setFill(cell.color)
                y += 1
            x += 1
