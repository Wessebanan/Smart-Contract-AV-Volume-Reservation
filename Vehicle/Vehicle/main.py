import Vehicle
import time
import random
import socket
import sys

random.seed(time.time())


def main(args):
    
    i = int(args[1])
    print('----------------\nVEHICLE INDEX: ' + str(i) + '\n----------------')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #while True:
    #    try:
    #        server.bind(('127.0.0.' + str(i + 1), i + 1))
    #    except:
    #        i = i + 1
    #        continue
    #    
    #    server.close()
    #    break

    vehicle = Vehicle.Vehicle(0, 0, i)

    frame_time = 0
    
    while True:
        frame_start = time.time()
        vehicle.update(frame_time)
        frame_end = time.time()
        frame_time = frame_end - frame_start


if __name__ == '__main__':
    main(sys.argv)