import socket
import threading
import contracts
import pickle
import time

# Debug, remove later
color_mapping = []
color_mapping.append("green")
color_mapping.append("blue")
color_mapping.append("red")
color_mapping.append("coral")
color_mapping.append("cyan")
color_mapping.append("gold")
color_mapping.append("pink")
color_mapping.append("brown")
color_mapping.append("yellow")
color_mapping.append("plum")

class RentedNode:
    def __init__(self, x, y, z, endTime):
        self.x = x
        self.y = y
        self.z = z
        self.endTime = endTime
    def checkRented(self):
        return self.endTime > time.time()
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'
    def __repr__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

class Peer:
    def __init__(self, index):
        self.index = index

        self.web3contract = contracts.Web3Contract('0x5B44e05f549988591aDb24ed02d3B8ce16E79d94', self.index)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = '127.0.0.' + str(index + 1)
        self.port = index + 1
        self.server.bind((self.ip, self.port))
        self.server_thread = threading.Thread(target=self.server_function)
        
        self.server_thread.start()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.free_nodes = []

    # Listens to incoming connections regarding node exchange.
    def server_function(self):
        while True:
            self.server.listen()
            while True:
                conn, addr = self.server.accept()
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    message = pickle.loads(data)

                    # Parse incoming message (list)
                    sender = message[0]
                    node = message[1:4]
                    exchange = message[4]
                    ip = ''
                    port = 0

                    if exchange:
                        ip = message[5]
                        port = message[6]

                    # Print information about message in the console.
                    info = ''
                    
                    color_index = int(conn.getsockname()[0][len(conn.getsockname()[0])-1]) - 1
                    info = info + (color_mapping[sender])
                    info = info + (' asked ')
                    info = info + (color_mapping[color_index])
                    if exchange:
                        info = info + (' to exchange node: ')
                    else:
                        info = info + (' for status of node: ')
                    info = info + (str(node))

                    # Check if the node is in the list of free (passed) nodes.
                    if node in self.free_nodes:
                        if exchange:
                            # Building and signing a transaction of the owner change and sending it over the socket.
                            signed_tx = self.web3contract.exchange_node(node[0], node[1], node[2], self.web3contract.address_from_id(sender), ip, port)
                            del self.free_nodes[self.free_nodes.index(node)]
                            conn.send(signed_tx)
                        conn.send(b'1')
                        info = info + (' SUCCESS')                       
                    # If node is not passed, it will not be exchanged.       
                    else:
                        conn.send(b'0')
                        info = info + (' FAILURE ')
                    print(info)
                    conn.close()
                    break  
    
    # Connects to specified socket (sockname = (ip: str, port: int)
    # and sends a request [id, x, y, z, exchange/check true/false]
    def message(self, sockname, message):    
        try:
            self.client.connect(sockname)  
        except:
            print('Could not contact about node: ' + str(message[:3]))
            print(sockname)
            return
        message.insert(0, self.index)
        self.client.send(pickle.dumps(message)) 
    
    # Asks owner if their node is available.
    def status_check(self, x, y, z):
        # Get owner for the taken node, check if this instance is the owner.
        owner = self.web3contract.get_owner(x, y, z)                    
        if owner_address == self.web3contract.web3.eth.defaultAccount:                        
            return True

        # Ask owner if the node is free.
        owner_sockname = (owner.ip, owner.port) 
        self.message(owner_sockname, [x, y, z, False])
        response = b''
        try:
            response = self.client.recv(1024)
        except:
            response = b'0'

        # Close the connection and remake socket to be able to connect to others.
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if response == b'':
            return False

        # Return the response.
        return bool(int(response))
    
    # Attempt to exchange the node with the owner.
    def exchange(self, x, y, z, seconds):
        owner = self.web3contract.get_owner(x, y, z)
        owner_address = owner.address
        if owner_address == self.web3contract.web3.eth.defaultAccount:                        
            return True

        # Ask owner to exchange the node.
        owner_sockname = (owner.ip, owner.port) 
        self.message(owner_sockname, [x, y, z, True, self.ip, self.port])
        
        try:
            response = self.client.recv(1024)
        except:
            return False

        if response == b'' or response == b'0':
            return False

        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Starting a thread that attempts to publish the transaction until it succeeds.
        threading.Thread(target=self.web3contract.send_transaction, args=(response,)).start()

        desired_end_time = int(time.time()) + seconds
        end_time = self.web3contract.get_end_time(x, y, z)
        
        time_to_add = desired_end_time - end_time
        if time_to_add > 0:
            result = self.web3contract.add_time(x, y, z, time_to_add)

            if not result:
                print('Could not add time to rental.')

        return True       

    def check_path(self, path, seconds):
        available = True

        start_time = time.time()
        end_time = start_time + seconds

        # Check if full path is available.
        for cell in path:
            x = int(cell.x)
            y = int(cell.y)
            z = 0
            # Ask contract if node is free.
            if not self.web3contract.check_available(x, y, z, start, end):
                # Ask owner if node might be exchanged.
                if not self.status_check(x, y, z):
                    available = False
                    break
        return available

    # Attempts to rent the nodes in path for given amount of time.
    def rent_path(self, rented_path, moving_path, seconds):
        rented = False
        path = moving_path.copy()

        while not rented:          
            
            # Rent path.
            rented = True
            
            start_time = int(time.time())
            end_time = start_time + seconds
            
            for cell in path:
                x = int(cell.x)
                y = int(cell.y)
                z = 0
            
                cell_success = True
                # Rent normally if available.
                if self.web3contract.check_available(x, y, z, start_time, end_time):
                    if not self.web3contract.rent_node(x, y, z, start_time, int(seconds), self.ip, self.port):                        
                        cell_success = False
                # Attempt exchange if not available.
                elif not self.exchange(x, y, z, seconds):
                    cell_success = False                    
                # Append cell to rented path if success.
                if cell_success:
                    rented_path.append(RentedNode(x, y, z, time.time()+seconds))
                    moving_path.append(cell)
                    del cell
                # Break otherwise
                else:
                    rented = False
                    break

            # Thread is done if full path was rented.
            if rented:
                return
            # Sleep for a bit to avoid excessive calls.
            else:
                time.sleep(10)
