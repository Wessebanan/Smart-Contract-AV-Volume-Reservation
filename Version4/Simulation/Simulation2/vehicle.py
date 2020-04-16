import socket
import threading
import pickle
import time

import graphics

POS_SIZE = 26

class GraphicalVehicle:
    def __init__(self, index, color, win):
        self.win = win
        self.index = index

        self.circle = graphics.Circle(graphics.Point(-20, -20), 20)
        self.circle.setWidth(5)
        self.circle.setFill(color)
        self.circle.draw(self.win)
        self.drawn = False

        self.color = color

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind(('127.0.0.1', 500 + self.index))
        self.receiver_thread = threading.Thread(target=self.receiver_function)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        
        self.new_pos = [-20, -20]

    def update(self):
        mvmt_x = self.new_pos[0] - self.circle.getCenter().getX()
        mvmt_y = self.new_pos[1] - self.circle.getCenter().getY()
        
        # Moving the circle according to the most recent position received.
        self.circle.move(mvmt_x, mvmt_y)

    def receiver_function(self):
        while True:
            self.receiver.listen()
            while True:
                conn, addr = self.receiver.accept()
                while True:
                    try:
                        data = bytearray()                       
                        while len(data) < POS_SIZE:
                            packet = conn.recv(POS_SIZE - len(data))
                            if not packet:
                                return
                            data.extend(packet)
                        conn.send(b'1')
                    except Exception as e:
                        return
                    
                    message = pickle.loads(data)

                    # Overwriting the new pos with the newest pos.
                    self.new_pos = message
