import socket
import threading
import contracts
import pickle
import time

lock = threading.Lock()

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

class Peer:
    def __init__(self, index):
        self.index = index

        self.web3contract = contracts.Web3Contract('0x243b5730647c70796cc6FdeC868bCCA7d199614f', self.index)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.' + str(index + 1), index + 1))
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
                            self.web3contract.exchange_node(node[0], node[1], node[2], self.web3contract.address_from_id(sender))
                            del self.free_nodes[self.free_nodes.index(node)]
                        conn.send(b'1')
                        info = info + (' SUCCESS')                       
                    # If node is not passed, it will not be exchanged.       
                    else:
                        conn.send(b'0')
                        info = info + (' FAILURE')
                    if exchange:
                        print(info)
                    conn.close()
                    break  
    
    # Connects to specified socket (sockname = (ip: str, port: int)
    # and sends a request [id, x, y, z, exchange/check true/false]
    def message(self, sockname, message):    
        try:
            self.client.connect(sockname)  
        except:
            return
        message.insert(0, self.index)
        self.client.send(pickle.dumps(message)) 
    
    # Attempts to rent the nodes in path for given amount of time.
    def rent_path(self, rented_path, path, seconds):
        rented = False

        while not rented:
            lock.acquire()            
            available = True

            # Check if full path is available.
            for cell in path:
                if not self.web3contract.contract.functions.CheckAvailable(int(cell.x), int(cell.y), 0).call():
                    
                    # Get owner for the taken node, check if this instance is the owner.
                    owner_address = self.web3contract.contract.functions.GetOwner(int(cell.x), int(cell.y), 0).call()                    
                    if owner_address == self.web3contract.web3.eth.defaultAccount:                        
                        continue

                    # Ask owner if the node is free.
                    owner_sockname = self.web3contract.sockname_from_address(owner_address)
                    self.message(owner_sockname, [int(cell.x), int(cell.y), 0, False])
                    response = b''
                    try:
                        response = self.client.recv(1024)
                    except:
                        response = b'0'

                    # Close the connection and remake socket to be able to connect to others.
                    self.client.close()
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    # If the node is not available to rent, break and wait a bit.
                    if not bool(int(response)):
                        available = False
                        break

            if available:
                # Rent path.
                rented = True
                
                for cell in path:
                    if self.web3contract.rent_node(int(cell.x), int(cell.y), 0, abs(seconds)):
                        rented_path.append(cell)
                    else:
                        owner_address = self.web3contract.contract.functions.GetOwner(int(cell.x), int(cell.y), 0).call()
                        if owner_address == self.web3contract.address_from_id(self.index):
                            rented_path.append(cell)
                            continue

                        owner_sockname = self.web3contract.sockname_from_address(owner_address)
                        self.message(owner_sockname, [int(cell.x), int(cell.y), 0, True])
                        
                        response = self.client.recv(1024)

                        self.client.close()
                        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                        # Check if the exchange was successful.
                        if bool(int(response)):

                            # If the remaining time of the rental was not enough, add more time.
                            remaining_time = self.web3contract.contract.functions.GetRemainingTime(int(cell.x), int(cell.y), 0).call()
                            if remaining_time < seconds:
                                tx_hash = self.web3contract.contract.functions.AddTimeToRental(int(cell.x), int(cell.y), 0, seconds - remaining_time).transact()
                                self.web3contract.web3.eth.waitForTransactionReceipt(tx_hash)
                            rented_path.append(cell)                   
                        else:
                            rented = False
                            break
            lock.release()
            if rented:
                return
            else:
                time.sleep(2) # Wait 10s to try again if failed.

