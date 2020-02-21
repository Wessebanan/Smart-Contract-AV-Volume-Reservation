import json
from web3 import Web3
from graphics import *
import sys

import simulation
import contracts
import vehicle


'''
    Difference being that ganache_url and address have
    to be passed as arguments from the command line.
'''
def main():

    # Set up web3 connection with Ganache.
    ganache_url = argv[1]
    web3 = Web3(Web3.HTTPProvider(ganache_url))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    abi = json.loads('[{"constant":true,"inputs":[],"name":"success","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_x","type":"int256"},{"name":"_y","type":"int256"},{"name":"_z","type":"int256"},{"name":"_duration","type":"uint256"}],"name":"RentNode","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"CheckSuccess","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"}]')
    address = web3.toChecksumAddress(argv[2])
    contract = web3.eth.contract(address=address, abi=abi)

    # Create window and set coordinate system.
    size_x = 1000
    size_y = 1000
    win = GraphWin("Grid", size_x, size_y, autoflush=False)
    win.setCoords(0,0,size_x,size_y)

    # Create, draw, and store grid.    
    grid_size_x = 10
    grid_size_y = 10
    grid = simulation.init_grid(size_x, size_y, grid_size_x, grid_size_y)
    simulation.draw_grid(win, grid)

    cell_size_x = size_x / grid_size_x
    cell_size_y = size_y / grid_size_y
    
    v1 = vehicle.Vehicle(550, 450, cell_size_x, cell_size_y, "red")
    path1 = v1.create_path(150, 50)
    v1.draw(win)

    v2 = vehicle.Vehicle(550, 50, cell_size_x, cell_size_y, "blue")
    path2 = v2.create_path(150, 550)
    v2.draw(win)

    rented_path1 = contracts.rent_path(path1, 60, contract, web3)
    rented_path2 = contracts.rent_path(path2, 60, contract, web3)

    simulation.color_path(win, grid, rented_path1, v1.getColor())
    simulation.color_path(win, grid, rented_path2, v2.getColor())
    
    frame_rate = 100
    frame_time = 1/frame_rate
    while True:
        update(frame_rate)
        v1.move(frame_time)
        v2.move(frame_time)
        if win.isClosed():
            break
    
main()
