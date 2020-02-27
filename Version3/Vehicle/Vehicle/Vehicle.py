import math
import peer
import threading
import time
import socket
import pickle
import random

# Sign helper function without having to import a whole new module.
def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

# Distance helper function
def dist(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)
def distP(p1,p2):
    return math.sqrt((p2.x-p1.x)**2+(p2.y-p1.y)**2)

def closest_corner_to_point(p, bl, tr):
    x = 0
    y = 0

    if abs(p.x - bl.x) > abs(p.x - tr.x):
        x = tr.x
    else:
        x = bl.x

    if abs(p.y - bl.y) > abs(p.y - tr.y):
        y = tr.y
    else:
        y = bl.y
    return x, y

# Helper class for coordinates.
class Vec2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    def dist(self, other):
        return math.sqrt((other.x-self.x)**2 + (other.x-self.x)**2)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
    def __repr__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'    

class Vehicle:
    def __init__(self, pos_x, pos_y, index, cell_size_x = 100, cell_size_y = 100, dimension_x = 20, dimension_y = 20, v = 20):
       
        # Index of the vehicle (for separate connections).
        self.index = index

        # Position and velocity relative to coordinate system.
        self.pos = Vec2(pos_x, pos_y)
        self.v = v

        # Goal position in coordinates.
        self.goal = Vec2(pos_x, pos_y)
        
        # Sockets for transmitting position information and receiving destinations.
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.settimeout(None)
        while True:
            try:
                self.sender.connect(('127.0.0.1', 500 + self.index))
            except socket.error as e:
                print(self.index, end=': ')
                print(e)
                continue           
            break        
        
        # Receive pos and goal from socket.
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind(('127.0.0.1', 100 + self.index))
        self.receiver_thread = threading.Thread(target=self.receiver_function)

       
        self.receiver_thread.start()
        self.receiver_thread.join()

        # Path in cells.
        self.cell_size = Vec2(cell_size_x, cell_size_y)
        self.cell = Vec2(math.floor(self.pos.x / self.cell_size.x), math.floor(self.pos.y / self.cell_size.y))
        self.path = []
        self.rented_path = []

        self.dimensions = Vec2(dimension_x, dimension_y)

        self.rent_thread = threading.Thread()
        self.time_per_cell = 60
        self.start_time = 0
        self.end_time = 0

        # Peer object for V2V communication.
        self.peer = peer.Peer(self.index)

        self.done = False
        self.rent_done = False

        self.create_path(self.goal.x, self.goal.y)
    
    def receiver_function(self):
        while True:
            self.receiver.listen()
            while True:
                conn, addr = self.receiver.accept()                
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    message = pickle.loads(data)
                    
                    # Set a position and create a path from the received message.
                    self.pos = Vec2(message[0], message[1])
                    self.goal = Vec2(message[2], message[3])
                    self.sender.sendall(pickle.dumps([self.pos.x, self.pos.y]))  
                    
                    conn.close()
                    break  
                break
            break
    # Reset function for when a vehicle has reached their goal.
    def reset(self):
        self.goal = Vec2(self.pos.x, self.pos.y)
        #self.path.clear()
        self.rent_thread = threading.Thread()
        self.start_time = 0
        self.end_time = 0

    
    def update(self, dt):
        # Do not update if vehicle reached the goal.
        if self.pos.dist(self.goal) < 0.01:
            return

        # Do not move if 'done'
        if self.done:
            return
               
        # Check if nodes have been exchanged.
        for cell in self.rented_path:
            if not cell.checkRented():
                del self.rented_path[self.rented_path.index(cell)]
            elif not [cell.x, cell.y, 0] in self.peer.free_nodes and not Vec2(cell.x, cell.y) in self.path:
                del self.rented_path[self.rented_path.index(cell)]

    
        # Move and transmit positional information.
        self.move(dt)        
        
        message = pickle.dumps([self.pos.x, self.pos.y])       
        sent = self.sender.send(pickle.dumps([self.pos.x, self.pos.y]))
        self.sender.recv(1024)        

    # Move towards goal, adjust movement if outside of path.
    def move(self, dt):        

        if len(self.path) <= 1:
            # If the path is empty and the vehicle is not at the goal, stop.
            if not self.get_cellP(self.goal) == self.cell:
                return       
        
        diff = self.goal - self.pos

        dist_to_goal = diff.length()

        cos = diff.x / dist_to_goal
        sin = diff.y / dist_to_goal

        mvmt_inc = self.v * dt
        mvmt = Vec2(mvmt_inc * cos, mvmt_inc * sin)   

        mvmt.x = sign(mvmt.x) * min(abs(mvmt.x), abs(self.goal.x - self.pos.x))
        mvmt.y = sign(mvmt.y) * min(abs(mvmt.y), abs(self.goal.y - self.pos.y))

        pos_copy = Vec2(self.pos.x, self.pos.y)

        self.pos = self.pos + mvmt
        
        self.adjust_movement(mvmt.x, mvmt.y)

        if dist_to_goal < 0.1:
            for cell in self.path:
                self.peer.free_nodes.append([cell.x, cell.y, 0])                
                del self.path[self.path.index(cell)]
            self.done = True
            self.reset()
            return
        
        # Check if vehicle has fully entered the next node in the path.
        bl = Vec2(self.pos.x - self.dimensions.x, self.pos.y - self.dimensions.y)
        br = Vec2(self.pos.x + self.dimensions.x, self.pos.y - self.dimensions.y)
        tl = Vec2(self.pos.x - self.dimensions.x, self.pos.y + self.dimensions.y)
        tr = Vec2(self.pos.x + self.dimensions.x, self.pos.y + self.dimensions.y)

        pts = [bl, br, tl, tr]

        if len(self.path) > 0:
            counter = 0
            for pt in pts:
                cpt = self.get_cellP(pt)
                if cpt.x == self.path[0].x and cpt.y == self.path[0].y:
                    break
                else:
                    counter += 1
            if counter == 4:
                free_node = [self.path[0].x, self.path[0].y, 0]
                self.peer.free_nodes.append(free_node)
                del self.path[0]

                if len(self.path) != 0:
                    self.cell.x = self.path[0].x
                    self.cell.y = self.path[0].y
    
    # Adjust movement if current position intersects a cell not in the path.
    def adjust_movement(self, mvmt_x, mvmt_y):
        # Getting the four points of the circles bounding box.
        bl = Vec2(self.pos.x - self.dimensions.x, self.pos.y - self.dimensions.y)
        br = Vec2(self.pos.x + self.dimensions.x, self.pos.y - self.dimensions.y)
        tl = Vec2(self.pos.x - self.dimensions.x, self.pos.y + self.dimensions.y)
        tr = Vec2(self.pos.x + self.dimensions.x, self.pos.y + self.dimensions.y)

        pts = [bl, br, tl, tr]

        adj_mvmt = Vec2()

        for pt in pts:
            if self.cell_in_pathP(self.get_cellP(pt)):
                continue
            # Get bl corner of cell where pt is.
            pt_cell = Vec2(math.floor(pt.x / self.cell_size.x) * 100, math.floor(pt.y / self.cell_size.y) * 100)
            
            # Find closest corner in cell relative to pt.
            x, y = closest_corner_to_point(pt, pt_cell, Vec2(pt_cell.x + self.cell_size.x, pt_cell.y + self.cell_size.y))

            if (len(self.path) > 1):
                direction = self.path[1] - self.path[0]
            else:
                direction = self.goal - self.pos
                direction.x /= direction.length()
                direction.y /= direction.length()
                                 
            # Adjust based on closest distance to closest corner.
            if abs(direction.x) < abs(direction.y):
                adj_mvmt.x = x - pt.x
                adj_mvmt.y = sign(mvmt_y) * (1 - abs(mvmt_y))
            else:
                adj_mvmt.y = y - pt.y
                adj_mvmt.x = sign(mvmt_x) * (1 - abs(mvmt_x))
            break

        self.pos.x += adj_mvmt.x
        self.pos.y += adj_mvmt.y   
    
    # Create the shortest path from current cell to goal cell.
    def create_path(self, goal_x, goal_y):        
        self.path.clear()
        
        self.goal.x = goal_x
        self.goal.y = goal_y
        
        goal_cell_x = math.floor(goal_x / self.cell_size.x)
        goal_cell_y = math.floor(goal_y / self.cell_size.y)

        current_cell_x = self.cell.x
        current_cell_y = self.cell.y
        
        self.path.append(Vec2(current_cell_x, current_cell_y))    

        dir_x = sign(goal_cell_x - current_cell_x)
        dir_y = sign(goal_cell_y - current_cell_y)
        
        while current_cell_x != goal_cell_x or current_cell_y != goal_cell_y:
            # Compare Euclidean distance between current and goal
            # for increments in both dimensions by direction.
            dist_x_inc = dist(current_cell_x + dir_x, current_cell_y, goal_cell_x, goal_cell_y)
            dist_y_inc = dist(current_cell_x, current_cell_y + dir_y, goal_cell_x, goal_cell_y)
            if dist_x_inc < dist_y_inc:
                current_cell_x += dir_x
            else:
                current_cell_y += dir_y
            self.path.append(Vec2(current_cell_x, current_cell_y))
        
        # Attempt to rent the calculated path.
        self.rent_thread = threading.Thread(target=self.peer.rent_path, args=(self.rented_path, self.path, self.time_per_cell,))
        self.rent_thread.daemon = True
        self.rent_thread.start()
        self.path.clear()
        return self.path   
    
    # Override the path.
    def set_path(self, path):
        self.path = path    

    # Conversion from coordinates to cell coordinates.
    def get_cell(self, x, y):
        return Vec2(math.floor(x / self.cell_size.x), math.floor(y / self.cell_size.y))
    def get_cellP(self, p):
        return Vec2(math.floor(p.x / self.cell_size.x), math.floor(p.y / self.cell_size.y))

    # Primitive solution to see if a cell is within the vehicle's path.
    def cell_in_path(self, cx, cy):
        for cell in self.path:
            if cell == Vec2(cx, cy):
                return True
        return False
    def cell_in_pathP(self, cp):
        for cell in self.path:
            if cell == cp:
                return True
        return False
