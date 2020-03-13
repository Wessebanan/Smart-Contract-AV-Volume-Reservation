import Vehicle
import time
import random
import socket
import sys

random.seed(time.time())


def main(args):
    if len(args) < 2:
        i = 0
    else:
        i = int(args[1])  

    vehicle = Vehicle.Vehicle(0, 0, i)

    # Static frame time to save performance 
    # (being a separate process taking as much performance as possible)s
    frame_time = 0.1
    
    while True:
        time.sleep(frame_time)
        try:
            vehicle.update(frame_time)            
        except:
            return


if __name__ == '__main__':

    main(sys.argv)