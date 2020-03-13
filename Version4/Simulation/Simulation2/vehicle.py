import socket
import threading
import pickle

import graphics

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

        self.pos_queue = []

    def update(self):
        if len(self.pos_queue) != 0:
            pos = self.pos_queue[0]
            mvmt_x = pos[0] - self.circle.getCenter().getX()
            mvmt_y = pos[1] - self.circle.getCenter().getY()

            self.circle.move(mvmt_x, mvmt_y)
            del self.pos_queue[0]

    def receiver_function(self):
        while True:
            self.receiver.listen()
            while True:
                conn, addr = self.receiver.accept()
                while True:
                    try:
                        data = conn.recv(4096)
                        conn.send(b'1')
                    except:
                        return
                    length = len(data)
                    if length == 26:
                        message = pickle.loads(data)

                        pos_x = message[0]
                        pos_y = message[1]
                        self.pos_queue.append([pos_x, pos_y])
