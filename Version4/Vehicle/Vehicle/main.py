import Vehicle
import time
import random
import socket
import sys

random.seed(time.time())

'''
MODES (args[2]):
0: Regular, all restricitons.
1: Always exchange.
2: No reservations.
3: Straight line.
'''


def main(args):
    i = 0
    mode = 0
    amount = 0
    if len(args) >= 2:
        i = int(args[1])
        if len(args) >= 3:
            mode = int(args[2])
            if len(args) == 4:
                amount = args[3]
            
    vehicle = Vehicle.Vehicle(0, 0, i, mode, amount)
  
    frame_time = 0.1

    while True:
        time.sleep(frame_time)
        
        vehicle.update(frame_time) 

        # Kill the process if the vehicle has no nodes to exchange and has reached its destination.
        if len(vehicle.rented_path) == 0 and vehicle.done:
            vehicle.update(frame_time) 
            #print(i, 'dead')
            return
            


if __name__ == '__main__':

    main(sys.argv)