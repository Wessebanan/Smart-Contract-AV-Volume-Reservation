import json
import web3
from web3.middleware import geth_poa_middleware
import time
import os
import threading

cd = os.path.dirname(__file__)
contract_path = os.path.join(cd, 'contractAddress.txt')

contract_address = ''
with open(contract_path) as f:
    contract_address = f.readline()
    #contract_address = contract_address[:len(contract_address) - 1]


cd = os.path.dirname(__file__)
json_path = os.path.join(cd, 'RentSpatialNode.json')

# Load the precompiled contract .json file.
truffleFile = json.load(open(json_path))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

class transacter:
    def __init__(self, index, n_transactions):
        self.ip = '127.0.0.1'
        self.port = 8500 + index
        self.n_transactions = n_transactions
        self.index = index
        self.w3 = web3.Web3(web3.Web3.HTTPProvider('http://' + self.ip + ':' + str(self.port)))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.w3.eth.defaultAccount = self.w3.eth.accounts[0]

        self.deployed_contract = self.w3.eth.contract(address=contract_address, abi = abi, bytecode = bytecode)

        self.thread = threading.Thread(target=self.transact)
        self.thread.start()

    def transact(self):
        hashes = []
        
        start = self.index * self.n_transactions
        x, y, z=start, start, start

        i = 0
        while i < self.n_transactions:
            tx_hash = self.deployed_contract.functions.RentNode(x,y,z,0,1,self.ip,self.port).transact()
            hashes.append(tx_hash)
            
            x = x + int((i+3) % 3 == 0)
            y = y + int((i+2) % 3 == 0)
            z = z + int((i+1) % 3 == 0)
           
            i+=1
        
        for hash in hashes:
            receipt = self.w3.eth.waitForTransactionReceipt(hash)
    
testers = []
for i in range(0,10):
    testers.append(transacter(i+1, 1000))

## First account becomes owner (port 8501)
#ip = 'http://127.0.0.1'
#port = '8501'

## Connect to the node.
#w3  = web3.Web3(web3.Web3.HTTPProvider(ip + ':' + port))

## Inject middleware to support PoA.
#w3.middleware_onion.inject(geth_poa_middleware, layer=0)

## Set defaultAccount to the only account in the node, for easy transactions.
#w3.eth.defaultAccount = w3.eth.accounts[0]



## Load the precompiled contract .json file.
#truffleFile = json.load(open('network/RentSpatialNode.json'))
#abi = truffleFile['abi']
#bytecode = truffleFile['bytecode']
#
## Contstruct the contract locally with abi and bytecode.
#local_contract = w3.eth.contract(abi=abi,bytecode=bytecode)
#
## Run the constructor as a transaction and wait for the transaction receipt.
#tx_hash = local_contract.constructor().transact()
#tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#
## Save the address of the contract.
#contract_address = tx_receipt.contractAddress
#
## Write contract address to file.
#with open('network/contractAddress.txt', 'w') as f:
#    f.write(contract_address)

#contractAddress = '0x86784C6901B42Dacf46b2e177cAD45B8af576FB5'
#deployed_contract = w3.eth.contract(address=contractAddress, abi=abi, bytecode=bytecode)

#nonce = int(w3.eth.getTransactionCount(w3.eth.defaultAccount))

#key_path = 'G:/devnet/node1/keystore/UTC--2020-03-09T09-48-01.070313300Z--27d3d4628b73172ab427e44cb59c8791efb79819'

#with open(key_path) as keyfile:
#    encrypted_key = keyfile.read()
#    private_key = w3.eth.account.decrypt(encrypted_key, 'pwdnode1')

##print(w3.isConnected())

#w3 = web3.Web3()
#print(w3.isConnected())

##w3  = web3.Web3(web3.Web3.HTTPProvider('http://' + ip + ':' + port))

##w3.eth.defaultAccount = w3.eth.accounts[0]

##print('SUCCESS')

#start = time.time()
#i=0

#hashes = []
#x,y,z=10000,10000,10000

#while i < 100:
#    tx = deployed_contract.functions.RentNode(x,y,z,0,60,ip,int(port)).buildTransaction()
#    tx.update({'nonce':nonce})
#    signed_tx = w3.eth.account.sign_transaction(tx,private_key=private_key)
#    raw_tx = signed_tx.rawTransaction
#    hashes.append(w3.eth.sendRawTransaction(raw_tx))
        
#    x = x + int((i+3) % 3 == 0)
#    y = y + int((i+2) % 3 == 0)
#    z = z + int((i+1) % 3 == 0)
#    #print((x,y,z))
#    i+=1
#    nonce+=1

#for hash in hashes:
#    receipt = w3.eth.waitForTransactionReceipt(hash)

#elapsed = time.time() - start
#print(elapsed/100)

#session = requests.Session()
#print(session)
#w3  = web3.Web3()
#pp = pprint.PrettyPrinter(indent=2)
#contractAddress='0x010f73E7d83f6dcFE7f55d66D97314347203F906'


#contract = w3.eth.contract(address='0x010f73E7d83f6dcFE7f55d66D97314347203F906', abi=abi, bytecode=bytecode)

#contract.functions.GetOwner(1,2,3).call()

#requestId = 0 # is automatically incremented at each request

#URL = 'http://localhost:8501' # url of my geth node
#PATH_GENESIS = 'G:/devnet/genesis/devnet.json'

## extracting data from the genesis file
#genesisFile = json.load(open(PATH_GENESIS))
#CHAINID = genesisFile['config']['chainId']
#PERIOD  = genesisFile['config']['clique']['period']
#GASLIMIT = int(genesisFile['gasLimit'],0)

## compile your smart contract with truffle first

## Don't share your private key !
#myAddress = '0x27d3d4628b73172ab427E44cB59C8791EFb79819' # address funded in genesis file

#cd_path = os.path.dirname(__file__)

#key_path = 'G:/devnet/node1/keystore/UTC--2020-03-09T09-48-01.070313300Z--27d3d4628b73172ab427e44cb59c8791efb79819'

#with open(key_path) as keyfile:
#    encrypted_key = keyfile.read()
#    myPrivateKey = w3.eth.account.decrypt(encrypted_key, 'pwdnode1')


##yPrivateKey = '0x94cb9f766ef067eb229da85213439cf4cbbcd0dc97ede9479be5ee4b7a93b96f'


#''' =========================== SOME FUNCTIONS ============================ '''
## see http://www.jsonrpc.org/specification
## and https://github.com/ethereum/wiki/wiki/JSON-RPC

#def createJSONRPCRequestObject(_method, _params, _requestId):
#    return {"jsonrpc":"2.0",
#            "method":_method,
#            "params":_params, # must be an array [value1, value2, ..., valueN]
#            "id":_requestId}, _requestId+1
    
#def postJSONRPCRequestObject(_HTTPEnpoint, _jsonRPCRequestObject):
#    response = session.post(_HTTPEnpoint,
#                            json=_jsonRPCRequestObject,
#                            headers={'Content-type': 'application/json'})

#    return response.json()

  
##''' ======================= DEPLOY A SMART CONTRACT ======================= '''
##### get your nonce
##requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionCount', [myAddress, 'latest'], requestId)
##responseObject = postJSONRPCRequestObject(URL, requestObject)
##myNonce = w3.toInt(hexstr=responseObject['result'])
##print('nonce of address {} is {}'.format(myAddress, myNonce))

##### create your transaction
##transaction_dict = {'from':myAddress,
##                    'to':'', # empty address for deploying a new contract
##                    'chainId':CHAINID,
##                    'gasPrice':1, # careful with gas price, gas price below the --gasprice option of Geth CLI will cause problems. I am running my node with --gasprice '1'
##                    'gas':2000000, # rule of thumb / guess work
##                    'nonce':myNonce,
##                    'data':bytecode} # no constrctor in my smart contract so bytecode is enough

##### sign the transaction
##signed_transaction_dict = w3.eth.account.signTransaction(transaction_dict, myPrivateKey)
##params = [signed_transaction_dict.rawTransaction.hex()]

##### send the transacton to your node
##requestObject, requestId = createJSONRPCRequestObject('eth_sendRawTransaction', params, requestId)
##responseObject = postJSONRPCRequestObject(URL, requestObject)
##transactionHash = responseObject['result']
##print('contract submission hash {}'.format(transactionHash))

##### wait for the transaction to be mined and get the address of the new contract
##while(True):
##    requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionReceipt', [transactionHash], requestId)
##    responseObject = postJSONRPCRequestObject(URL, requestObject)
##    receipt = responseObject['result']
##    if(receipt is not None):
##        if(receipt['status'] == '0x1'):
##            contractAddress = receipt['contractAddress']
##            print('newly deployed contract at address {}'.format(contractAddress))
##        else:
##            pp.pprint(responseObject)
##            raise ValueError('transacation status is "0x0", failed to deploy contract. Check gas, gasPrice first')
##        break
##    time.sleep(PERIOD/10)
#contractAddress='0x010f73E7d83f6dcFE7f55d66D97314347203F906'


#''' ================= SEND A TRANSACTION TO SMART CONTRACT  ================'''
#### get your nonce
#requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionCount', [myAddress, 'latest'], requestId)
#responseObject = postJSONRPCRequestObject(URL, requestObject)
#myNonce = w3.toInt(hexstr=responseObject['result'])
#print('nonce of address {} is {}'.format(myAddress, myNonce))

#### prepare the data field of the transaction
## function selector and argument encoding
## https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding
#x, y, z = 1, 3, 2 # random numbers here
#function = 'GetOwner(int256,int256,int256)' # from smart contract
#methodId = w3.sha3(text=function)[0:9].hex()
#param1 = (x).to_bytes(32, byteorder='big').hex()
#param2 = (y).to_bytes(32, byteorder='big').hex()
#param3 = (z).to_bytes(32, byteorder='big').hex()
#data = '0x' + methodId + param1 + param2 + param3

#transaction_dict = {'from':myAddress,
#                    'to':contractAddress,
#                    'chainId':CHAINID,
#                    'gasPrice':1, # careful with gas price, gas price below the threshold defined in the node config will cause all sorts of issues (tx not bieng broadcasted for example)
#                    'gas':2000000, # rule of thumb / guess work
#                    'nonce':myNonce}
##,
##                    'data':data}

#### sign the transaction
#signed_transaction_dict = w3.eth.account.signTransaction(transaction_dict, myPrivateKey)
#params = [signed_transaction_dict.rawTransaction.hex()]

#### send the transacton to your node
#print('executing {} with value {},{}'.format(function, x, y, z))
#requestObject, requestId = createJSONRPCRequestObject('eth_sendRawTransaction', params, requestId)
#responseObject = postJSONRPCRequestObject(URL, requestObject)
#transactionHash = responseObject['result']
#print('transaction hash {}'.format(transactionHash))

#### wait for the transaction to be mined
#while(True):
#    requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionReceipt', [transactionHash], requestId)
#    responseObject = postJSONRPCRequestObject(URL, requestObject)
#    receipt = responseObject['result']
#    if(receipt is not None):
#        if(receipt['status'] == '0x1'):
#            print('transaction successfully mined')
#        else:
#            pp.pprint(responseObject)
#            raise ValueError('transacation status is "0x0", failed to deploy contract. Check gas, gasPrice first')
#        break
#    time.sleep(PERIOD/10)



#''' ============= READ YOUR SMART CONTRACT STATE USING GETTER  =============='''
## we don't need a nonce since this does not create a transaction but only ask
## our node to read it's local database

#### prepare the data field of the transaction
## function selector and argument encoding
## https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding
## state is declared as public in the smart contract. This creates a getter function
#methodId = w3.sha3(text='state()')[0:4].hex()
#data = '0x' + methodId
#transaction_dict = {'from':myAddress,
#                    'to':contractAddress,
#                    'chainId':CHAINID,
#                    'data':data}

#params = [transaction_dict, 'latest']
#requestObject, requestId = createJSONRPCRequestObject('eth_call', params, requestId)
#responseObject = postJSONRPCRequestObject(URL, requestObject)
#state = w3.toInt(hexstr=responseObject['result'])
#print('using getter for public variables: result is {}'.format(state))



#''' ============= READ YOUR SMART CONTRACT STATE GET FUNCTIONS  =============='''
## we don't need a nonce since this does not create a transaction but only ask
## our node to read it's local database

#### prepare the data field of the transaction
## function selector and argument encoding
## https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding
## state is declared as public in the smart contract. This creates a getter function
#methodId = w3.sha3(text='getState()')[0:4].hex()
#data = '0x' + methodId
#transaction_dict = {'from':myAddress,
#                    'to':contractAddress,
#                    'chainId':CHAINID,
#                    'data':data}

#params = [transaction_dict, 'latest']
#requestObject, requestId = createJSONRPCRequestObject('eth_call', params, requestId)
#responseObject = postJSONRPCRequestObject(URL, requestObject)
#state = w3.toInt(hexstr=responseObject['result'])
#print('using getState() function: result is {}'.format(state))


#''' prints
#nonce of address 0xF464A67CA59606f0fFE159092FF2F474d69FD675 is 4
#contract submission hash 0x64fc8ce5cbb5cf822674b88b52563e89f9e98132691a4d838ebe091604215b25
#newly deployed contract at address 0x7e99eaa36bedba49a7f0ea4096ab2717b40d3787
#nonce of address 0xF464A67CA59606f0fFE159092FF2F474d69FD675 is 5
#executing add(uint256,uint256) with value 10,32
#transaction hash 0xcbe3883db957cf3b643567c078081343c0cbd1fdd669320d9de9d05125168926
#transaction successfully mined
#using getter for public variables: result is 42
#using getState() function: result is 42
#'''


##method = 'eth_getTransactionCount'
##params = ["0x27d3d4628b73172ab427E44cB59C8791EFb79819","latest"]
##PAYLOAD = {"jsonrpc":"2.0",
##           "method":method,
##           "params":params,
##           "id":67}
##PAYLOAD = json.dumps(PAYLOAD)

##headers = {'Content-type': 'application/json'}
##response = session.post('http://127.0.0.1:8501', data=PAYLOAD, headers=headers)
##print(response.content)
##json.loads(response.content)['result']

##w3 = Web3(Web3.HTTPProvider("127.0.0.1:30310"))

##print(w3.isConnected())


##connected = w3.isConnected()

##if connected and w3.clientVersion.startswith('Parity'):
##    enode = w3.parity.enode

##elif connected and w3.clientVersion.startswith('Geth'):
##    enode = w3.geth.admin.nodeInfo['enode']

##else:
##    enode = None

##node1:
##0x27d3d4628b73172ab427E44cB59C8791EFb79819
##
##node2:
##0x800D55ffd2d9C470dbd847703f8FE23a4ad9c57D
