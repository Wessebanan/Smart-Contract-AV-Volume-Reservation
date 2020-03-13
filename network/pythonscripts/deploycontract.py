import json
import web3
from web3.middleware import geth_poa_middleware
import os

# Node1 becomes owner (port 8501)
ip = 'http://127.0.0.1'
port = '8501'

# Connect to the node.
w3  = web3.Web3(web3.Web3.HTTPProvider(ip + ':' + port))

# Inject middleware to support PoA.
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Set defaultAccount to the only account in the node, for easy transactions.
w3.eth.defaultAccount = w3.eth.accounts[0]

cd = os.path.dirname(__file__)
json_path = os.path.join(cd, '../info/RentSpatialNode.json')

# Load the precompiled contract .json file.
truffleFile = json.load(open(json_path))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

# Contstruct the contract locally with abi and bytecode.
local_contract = w3.eth.contract(abi=abi,bytecode=bytecode)

# Run the constructor as a transaction and wait for the transaction receipt.
tx_hash = local_contract.constructor().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Save the address of the contract.
contract_address = tx_receipt.contractAddress

# Write contract address to file.
file_path = os.path.join(cd, '../info/contractAddress.txt')
with open(file_path, 'w') as f:
    f.write(contract_address)
