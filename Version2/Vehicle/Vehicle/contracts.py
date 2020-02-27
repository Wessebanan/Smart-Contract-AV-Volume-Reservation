import json
from web3 import Web3
import os

class Web3Contract:
    def __init__(self, address, index):

        self.index = index
        self.nonce = 0

        # Setup connection to smart contract at @param address with locally stored abi.
        url = "http://127.0.0.1:8545"
        self.web3 = Web3(Web3.HTTPProvider(url))
        self.web3.eth.defaultAccount = self.web3.eth.accounts[index]
       
        cd_path = os.path.dirname(__file__)
        file_path = os.path.join(cd_path, '../../RentSpatialNode.json')
 
        with open(file_path) as f:
            abi = json.load(f)
        self.contract = self.web3.eth.contract(address=address, abi=abi)

        # Store private key for signing transactions in a very unsafe manner.
        private_key_path = os.path.join(cd_path, '../ganache_private_keys.txt')
        with open(private_key_path) as f:
            i = 0
            while i < index:
                f.readline()
                i = i + 1
            self.private_key = f.readline()
        self.private_key = self.private_key[:len(self.private_key)-1]

    # Rent a free node if available.
    def rent_node(self, x, y, z, seconds):
        tx_hash = self.contract.functions.RentNode(x,y,z,seconds).transact()
        tx_data = self.web3.eth.waitForTransactionReceipt(tx_hash)['logs'][0]['data']
        return bool(int(tx_data, 16))
    
    # Build and sign a transaction transferring the ownership to newOwner.
    def exchange_node(self, x, y, z, newOwner):
        
        tx = self.contract.functions.ChangeOwner(x,y,z,newOwner).buildTransaction()
        tx.update({'nonce' : self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount) })
        
        signed_tx = self.web3.eth.account.signTransaction(tx, self.private_key)
        return signed_tx.rawTransaction


    # Converts the eth address to the p2p ip (temp?)
    def sockname_from_address(self, address):
        if address in self.web3.eth.accounts:
            index = self.web3.eth.accounts.index(address) + 1
            sockname = ('127.0.0.' + str(index), index)
            return sockname
        else:
            return ('',-1)

    def address_from_id(self, id):        
        if id < len(self.web3.eth.accounts):
            return self.web3.eth.accounts[id]
        else:
            print('Bad index: ' + str(id))
            return -1