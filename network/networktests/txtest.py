import json
import web3
from web3.middleware import geth_poa_middleware
import time
import os
import threading

cd = os.path.dirname(__file__)
contract_path = os.path.join(cd, '../info/contractAddress.txt')

contract_address = ''
with open(contract_path) as f:
    contract_address = f.readline() 

cd = os.path.dirname(__file__)
json_path = os.path.join(cd, '../info/RentSpatialNode.json')

# Load the precompiled contract .json file.
truffleFile = json.load(open(json_path))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

ip = '127.0.0.1'
port = 8551
w3 = web3.Web3(web3.Web3.HTTPProvider('http://' + ip + ':' + str(port)))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.defaultAccount = w3.eth.accounts[0]

deployed_contract = w3.eth.contract(address = contract_address, abi = abi, bytecode = bytecode)

#w32 = web3.Web3(web3.Web3.HTTPProvider('http://' + ip + ':' + str(port+1)))
#w32.middleware_onion.inject(geth_poa_middleware, layer=0)
#w32.eth.defaultAccount = w32.eth.accounts[0]

#deployed_contract2 = w32.eth.contract(address = contract_address, abi = abi, bytecode = bytecode)

#owner = deployed_contract.functions.GetOwner(0,0,0).call()
#print(owner)
#tx_hash = deployed_contract.functions.RentNode(1,2,3,0,10,ip,port).transact()
#tx_hash2 = deployed_contract.functions.RentNode(1,2,3,0,10,ip,port+1).transact()
#w3.eth.waitForTransactionReceipt(tx_hash)
#w3.eth.waitForTransactionReceipt(tx_hash2)
#owner = deployed_contract.functions.GetOwner(0,0,0).call()
#print(owner)

block = w3.eth.getBlock(3613)
print(w3.eth.blockNumber)
#print(w3.eth.getBlockTransactionCount('latest'))

for tx in block.transactions:
    #print(w3.eth.getTransaction(tx))
    tx_info = w3.eth.getTransaction(tx)
    
    tx_receipt = w3.eth.getTransactionReceipt(tx_info.hash)

    input = deployed_contract.decode_function_input(tx_info['input'])
    params = input[1]

    x = params['_x']
    y = params['_y']
    z = params['_z']

    hexresult = tx_receipt['logs'][0]['data']
    result = bool(int(hexresult,16))

    print(tx_info['from'])
    print(x, y, z)
    print(result)



start = time.time()
for i in range(0,100):
    deployed_contract.functions.GetOwner(0,0,0).call()
print(time.time() - start)

#16 ms 60/s 

#print(w3.eth.blockNumber)
#print(int(w3.eth.blockNumber))

#block = w3.eth.getBlock(w3.eth.blockNumber)
#txs = block.transactions



#tx = w3.eth.getTransaction(tx_hash)
#receipt = w3.eth.getTransactionReceipt(tx_hash)
#hexresult = receipt['logs'][0]['data']
#result = bool(int(hexresult,16))
##tx_data = self.web3.eth.waitForTransactionReceipt(tx_hash)['logs'][0]['data']
##        return bool(int(tx_data, 16))
#
#input = deployed_contract.decode_function_input(tx['input'])
#print(input)
#print(result)
