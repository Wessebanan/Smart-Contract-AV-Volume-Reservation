import random
import time
import socket
import pickle
import sys
import os
import threading

import simulation

random.seed(time.time())

routes = []

for i in range(0,5):
    x = 5-i
    y = 0
    z = x+3
    w = 9
    routes.append([x, y, z, w])
    routes.append([y, x, w, z])


def spawn_vehicles(sim, amount, mode):
    grid_size_x = sim.grid_size_x
    grid_size_y = sim.grid_size_y

    cell_size_x = sim.cell_size_x
    cell_size_y = sim.cell_size_y

    n_vehicles = len(sim.vehicles)
    i = n_vehicles

    while i < amount + n_vehicles and i < 10:
        sim.add_vehicle(mode, amount)

        start_x = random.randint(0, grid_size_x - 1) * cell_size_x + cell_size_x / 2
        start_y = random.randint(0, grid_size_y - 1) * cell_size_y + cell_size_y / 2

        goal_x = random.randint(0, grid_size_x - 1) * cell_size_x + cell_size_x / 2
        goal_y = random.randint(0, grid_size_y - 1) * cell_size_y + cell_size_y / 2

        #start_x = routes[i][0] * cell_size_x + cell_size_x / 2
        #start_y = routes[i][1] * cell_size_y + cell_size_y / 2
        #          
        #goal_x = routes[i][2] * cell_size_x + cell_size_x / 2
        #goal_y = routes[i][3] * cell_size_y + cell_size_y / 2

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                sock.connect(('127.0.0.1', 100 + i))
            except:
                print('cant connect to index ' + str(i))
                continue
            break
        sock.sendall(pickle.dumps([start_x, start_y, goal_x, goal_y]))
        #sock.sendall(pickle.dumps(routes[i]))
        sock.close()

        i += 1

def main():

    n_vehicles = 4
    mode = 2
    if len(sys.argv) >= 2:
        n_vehicles = int(sys.argv[1])
        if len(sys.argv) == 3:
            mode = sys.argv[2]
    
    print('Running with ', n_vehicles, ' vehicles in mode ', mode)
    # Create window and set coordinate system.
    size_x = 1000
    size_y = 1000
    grid_size_x = 10
    grid_size_y = 10
    
    sim = simulation.Simulation(size_x, size_y, grid_size_x, grid_size_y)
    spawn_vehicles(sim, n_vehicles, mode)
    sim.win.close()
    del sim
    #return
    
    while True:
        time.sleep(5)
        if threading.active_count() == 1:
            return



    frame_time = 0
    frame_start = time.time()

    while True:
        if frame_time < 1 / 1000:
            frame_time = time.time() - frame_start
        else:
            frame_start = time.time()
            sim.update(frame_time)
        if not sim.open:
            break

main()
