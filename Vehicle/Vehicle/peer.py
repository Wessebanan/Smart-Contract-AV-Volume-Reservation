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

        self.web3contract = contracts.Web3Contract('0x92ce6a4723d8F0D84ef3Aee87fb082Edb9592D2e', self.index)

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
                            # Building and signing a transaction of the owner change and sending it over the socket.
                            signed_tx = self.web3contract.exchange_node(node[0], node[1], node[2], self.web3contract.address_from_id(sender))
                            del self.free_nodes[self.free_nodes.index(node)]
                            conn.send(signed_tx)
                        conn.send(b'1')
                        info = info + (' SUCCESS')                       
                    # If node is not passed, it will not be exchanged.       
                    else:
                        conn.send(b'0')
                        info = info + (' FAILURE ')
                        #info = info + ' Free nodes: ' + str(self.free_nodes)
                        remaining_time = self.web3contract.contract.functions.GetRemainingTime(node[0], node[1], node[2]).call()
                        info = info + str(remaining_time)
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
        
        if response == b'':
            return False

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

        if response == b'' or response == b'0':
            return False

        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Publish the transaction stating the owner change, having the transaction signed as a guarantee.
        tx = response
        tx_hash = self.web3contract.web3.eth.sendRawTransaction(tx)
        self.web3contract.web3.eth.waitForTransactionReceipt(tx_hash)

        remaining_time = self.web3contract.contract.functions.GetRemainingTime(x, y, z).call()
        if remaining_time < seconds:
            tx_hash = self.web3contract.contract.functions.AddTimeToRental(x, y, z, seconds - remaining_time).transact()
            self.web3contract.web3.eth.waitForTransactionReceipt(tx_hash)
        return True
        
    
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
    def rent_path(self, rented_path, moving_path, seconds):
        rented = False
        path = moving_path.copy()

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
                        available = False
                        break

            if available:
                # Rent path.
                rented = True

                for cell in path:
                    x = int(cell.x)
                    y = int(cell.y)
                    z = 0

                    cell_success = True
                    # Rent normally if available.
                    if self.web3contract.contract.functions.CheckAvailable(x, y, z).call():
                        if not self.web3contract.rent_node(x, y, z, abs(seconds)):                        
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

            if rented:
                return
            #else:
            #    time.sleep(10) # Wait 10s to try again if failed.

