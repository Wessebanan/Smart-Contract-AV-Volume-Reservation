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

class Peer:
    def __init__(self, index):
        self.index = index

        self.web3contract = contracts.Web3Contract('0xf556B1FD9Eb18cb8E3ad3BfdF1Bb069359fC38b5', self.index)

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
                            #print('Attempting to exchange node: ' + str(node) + ' to ' + self.web3contract.address_from_id(sender) + ' from ' + self.web3contract.address_from_id(self.index))
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
            print('Could not contact about node: ' + str(message[:3]))
            #print('VEHICLE TRIED TO CONNECT TO OTHER VEHICLE OOPSIE POOPSIE')
            return
        message.insert(0, self.index)
        self.client.send(pickle.dumps(message)) 
    
    # Asks owner if their node is available.
    def status_check(self, x, y, z):
        # Get owner for the taken node, check if this instance is the owner.
        owner_address = self.web3contract.contract.functions.GetOwner(x, y, z).call()                    
        if owner_address == self.web3contract.web3.eth.defaultAccount:                        
            return True

        # Ask owner if the node is free.
        owner_sockname = self.web3contract.sockname_from_address(owner_address)
        self.message(owner_sockname, [x, y, z, False])
        response = b''
        try:
            response = self.client.recv(1024)
        except:
            response = b'0'

        # Close the connection and remake socket to be able to connect to others.
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Return the response.
        return bool(int(response))
    
    # Attempt to exchange the node with the owner.
    def exchange(self, x, y, z, seconds):
        owner_address = self.web3contract.contract.functions.GetOwner(x, y, z).call()
        if owner_address == self.web3contract.address_from_id(self.index):
            return True

        owner_sockname = self.web3contract.sockname_from_address(owner_address)
        self.message(owner_sockname, [x, y, z, True])
        
        try:
            response = self.client.recv(1024)
        except:
            return False

        if response == b'':
            return False

        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Check if the exchange was successful.
        if bool(int(response)):
            # If the remaining time of the rental was not enough, add more time.
            remaining_time = self.web3contract.contract.functions.GetRemainingTime(x, y, z).call()
            if remaining_time < seconds:
                tx_hash = self.web3contract.contract.functions.AddTimeToRental(x, y, z, seconds - remaining_time).transact()
                self.web3contract.web3.eth.waitForTransactionReceipt(tx_hash)
            return True                  
        else:
            return False
    
    # Return rented nodes in case of failure in full path rental.
    def return_nodes(self, path):
        for cell in path:
            x = int(cell.x)
            y = int(cell.y)
            z = 0

            # Attempt transaction and wait for receipt.
            tx_hash = self.web3contract.contract.functions.ReturnNode(x, y, z).transact()
            self.web3contract.web3.eth.waitForTransactionReceipt(tx_hash)
            if not self.web3contract.contract.functions.CheckAvailable(x,y,z).call():
                return False
        return True


    # Attempts to rent the nodes in path for given amount of time.
    def rent_path(self, rented_path, path, seconds):
        rented = False

        while not rented:           
            available = True

            # Check if full path is available.
            for cell in path:
                x = int(cell.x)
                y = int(cell.y)
                z = 0
                # Ask contract if node is free.
                if not self.web3contract.contract.functions.CheckAvailable(x, y, z).call():
                    # Ask owner if node might be exchanged.
                    if not self.status_check(x, y, z):
                        break

            if available:
                # Rent path.
                rented = True
                #print('Trying to rent...')
                for cell in path:
                    x = int(cell.x)
                    y = int(cell.y)
                    z = 0

                    cell_success = True
                    # Rent normally if available.
                    if self.web3contract.contract.functions.CheckAvailable(x, y, z).call():
                        if self.web3contract.rent_node(x, y, z, abs(seconds)):
                            rented_path.append(cell)
                            #print('Rented: ' + str(cell))
                        else:
                            cell_success = False

                    # Attempt exchange if not available.
                    elif self.exchange(x, y, z, seconds):
                        rented_path.append(cell)
                        #print('Exchanged: ' + str(cell))
                    # Stop if failure.
                    else:
                        cell_success = False
                    
                    # Return rented nodes if any node in path fails.
                    if not cell_success:
                        rented = False
                        print('Failed to rent: ' + str(cell))
                        address = self.web3contract.contract.functions.GetOwner(x,y,z).call()
                        sockname = self.web3contract.sockname_from_address(address)
                        try:
                            print('Owner is: ' + color_mapping[int(sockname[0][len(sockname[0])-1]) - 1])
                        except:
                            print('---------------------')
                            print(sockname)
                            print('---------------------')
                        result = self.return_nodes(rented_path)
                        if not result:
                            print('failed in returning path')
                        rented_path.clear()
                        break

            if rented:
                #print('Full path rented.')
                return
            #else:
            #    time.sleep(10) # Wait 10s to try again if failed.

