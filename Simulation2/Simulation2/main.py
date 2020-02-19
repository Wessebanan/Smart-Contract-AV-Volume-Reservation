import random
import time
import simulation
import socket
import pickle

random.seed(time.time())


def spawn_vehicles(sim, amount):
    grid_size_x = sim.grid_size_x
    grid_size_y = sim.grid_size_y

    cell_size_x = sim.cell_size_x
    cell_size_y = sim.cell_size_y

    n_vehicles = len(sim.vehicles)
    i = n_vehicles

    while i < amount + n_vehicles and i < 10:    
        sim.add_vehicle()

        start_x = random.randint(0, grid_size_x - 1) * cell_size_x + cell_size_x / 2
        start_y = random.randint(0, grid_size_y - 1) * cell_size_y + cell_size_y / 2

        goal_x = random.randint(0, grid_size_x - 1) * cell_size_x + cell_size_x / 2
        goal_y = random.randint(0, grid_size_y - 1) * cell_size_y + cell_size_y / 2

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                sock.connect(('127.0.0.1', 100 + i))
            except:
                continue           
            break
        
        sock.send(pickle.dumps([start_x, start_y, goal_x, goal_y]))
        sock.close()

        i+=1

def main():
    # Create window and set coordinate system.
    size_x = 1000
    size_y = 1000
    grid_size_x = 10
    grid_size_y = 10   
    
    frame_rate = 100
    frame_time = 1/frame_rate

    sim = simulation.Simulation(size_x, size_y, grid_size_x, grid_size_y, frame_rate)
    
    spawn_vehicles(sim, 10)

    start_time = time.time()

    while True:
        sim.update(frame_time)

        elapsed_time = time.time() - start_time

        if elapsed_time > 10.0:
            start_time = time.time()
            #spawn_vehicles(sim, 1)

        if not sim.open:
            break
    
main()