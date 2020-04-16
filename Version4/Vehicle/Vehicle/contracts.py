import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import time

class Actor:
    def __init__(self, address, ip, port, priority):
        self.address = address
        self.ip = ip
        self.port = port
        self.priority = priority

class Web3Contract:
    def __init__(self, index, mode):

        self.index = index + 1
        self.port = 8500 + self.index

        # Setup connection to smart contract at @param address with locally stored abi.
        url = "http://127.0.0.1:" + str(self.port)
        self.web3 = Web3(Web3.HTTPProvider(url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]

        # Track nonce locally for offline transactions.
        self.nonce = self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount)
       
        cd_path = os.path.dirname(__file__)
        json_path = os.path.join(cd_path, '../../../network/info/RentSpatialNode.json')
        contract_address_path = os.path.join(cd_path, '../../../network/info/contractAddress.txt')

        # Fetch contract info from files.
        with open(contract_address_path) as f:
            address = f.readline()
            
        with open(json_path) as f:
            json_file   = json.load(f)
            abi         = json_file['abi']
            bytecode    = json_file['bytecode']

        # Build contract from info.
        self.contract = self.web3.eth.contract(address=address, abi=abi, bytecode=bytecode)
       
        # Fetch and store private key for offline signing.        

        # Open info file with account addresses and keyfile paths.
        account_list_path = os.path.join(cd_path, '../../../network/info/account_list.txt')
        password_file_path = os.path.join(cd_path, '../../../network/info/password.txt')

        # Reading relevant info from files.
        with open(password_file_path) as password_file:
            password = password_file.readline()

        with open(account_list_path) as account_list:
            for i in range(0, self.index * 2):
                keyfile_path = account_list.readline()
            keyfile_path = keyfile_path.strip('\n')
            nodes_dir_path = os.path.join(cd_path, '../../../network/nodes')
            keyfile_path = os.path.join(nodes_dir_path, keyfile_path)

        with open(keyfile_path) as keyfile:
            encrypted_key = keyfile.read()
            self.private_key = self.web3.eth.account.decrypt(encrypted_key, password)

        

    # Rent a free node if available.
    def rent_node(self, x, y, z, start, duration, ip, port):
        info = str(self.index) + ' before rent_node: ' + str(self.nonce)
        while True:
            try:
                tx_hash = self.contract.functions.RentNode(x,y,z,start,duration,ip,port).transact({'nonce' : self.nonce })
                break
            except Exception as e:
                print('rent_node except: ', e)
                time.sleep(5)
       
        self.nonce += 1
        info += ' after rent_node: ' + str(self.nonce)
        #print(info)
        tx_data = self.web3.eth.waitForTransactionReceipt(tx_hash)['logs'][0]['data']
        tx_result = bool(int(tx_data, 16))

        return tx_result
    
    # Build and sign a transaction transferring the ownership to newOwner.
    def exchange_node(self, x, y, z, newOwner, ip, port): 
        info = str(self.index) + ' before exchange: ' + str(self.nonce)
        tx = self.contract.functions.ChangeOwner(x, y, z, newOwner, ip, port).buildTransaction({'nonce' : self.nonce })
        signed_tx = self.web3.eth.account.signTransaction(tx, self.private_key)
        self.nonce += 1       
        info += ' after exchange: ' + str(self.nonce)
        #print(info)
        return signed_tx.rawTransaction

    # Assumes time is added to the current active rental.
    def add_time(self, x, y, z, seconds):        
        # Check that the node is available for the time being added.
        end_time = self.contract.functions.GetEndTime(x, y, z).call()
        available = self.contract.functions.CheckAvailable(x, y, z, end_time, end_time + seconds).call()
        
        # Add time if the node is available.
        if available:
            tx_hash = self.contract.functions.AddTimeToRental(x, y, z, seconds).transact()
            self.web3.eth.waitForTransactionReceipt(tx_hash)

        return available

    # Retrieves a tuple from the contract with the current owner information.
    # Builds an Actor object from the information and returns it.
    def get_owner(self, x, y, z):
        owner = self.contract.functions.GetOwner(x, y, z).call()
        actor = Actor(owner[0], owner[1], owner[2], owner[3])

        return actor

    # Attempts to send a signed raw transaction until it succeeds (for threading).
    def send_transaction(self, tx):
        while True:
            try:                
                tx_hash = self.web3.eth.sendRawTransaction(tx)
                tx_data = self.web3.eth.waitForTransactionReceipt(tx_hash)
                break
            except Exception as e:
                print(e)
                time.sleep(10)
                continue
    
    # Returns the end time of the current rental from the contract.
    def get_end_time(self, x, y, z):
        return self.contract.functions.GetEndTime(x, y, z).call()

    def check_available(self, x, y, z, start, end):
        return self.contract.functions.CheckAvailable(x, y, z, int(start), int(end)).call()
