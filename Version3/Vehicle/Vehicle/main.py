import Vehicle
import time
import random
import socket
import sys

random.seed(time.time())


def main(args):
    
    i = int(args[1])  

    vehicle = Vehicle.Vehicle(0, 0, i)

    frame_time = 0
    frame_start = time.time()

    while True:
        #if vehicle.done:
        #    break
        if frame_time < 1 / 10:
            frame_time = time.time() - frame_start
        else:
            try:
                vehicle.update(frame_time)
                frame_time = 0
                frame_start = time.time()       
            except:
                return


if __name__ == '__main__':

    main(sys.argv)