import graphics
import socket
import threading
import pickle

class GraphicalVehicle:
    def __init__(self, index, color, win):
        self.win = win
        self.index = index
        
        self.circle = graphics.Circle(graphics.Point(0, 0), 20)
        self.circle.setWidth(5)
        self.circle.setFill(color)
        self.circle.draw(self.win)        
        self.drawn = False

        self.color = color

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind(('127.0.0.1', 500 + self.index))
        self.receiver_thread = threading.Thread(target=self.receiver_function)
        self.receiver_thread.start()
        self.mvmt_x = 0
        self.mvmt_y = 0

    def update(self):
        if self.mvmt_x != 0 or self.mvmt_y != 0:
            self.circle.move(self.mvmt_x, self.mvmt_y)
            self.mvmt_x = 0
            self.mvmt_y = 0

    def receiver_function(self):
        while True:
            self.receiver.listen()
            while True:
                conn, addr = self.receiver.accept()                
                while True:
                    data = conn.recv(4096)
                    length = len(data)
                    if length == 26:
                        #break
                        message = pickle.loads(data)
                        #print(message)
                        # Move circle to where the vehicle currently is.
                        self.mvmt_x = message[0] - self.circle.getCenter().getX()
                        self.mvmt_y = message[1] - self.circle.getCenter().getY()                                      
                    
                    #conn.close()
                    #break  

