import os
import threading
import subprocess

def start(c):
    #t = threading.Thread(target=os.system, args=('cmd /c ' + c,))
    t = subprocess.Popen('start ' + c, shell=True)
    #t.start()
    return t

# Storing each address in this list.
sealer_addresses = []
node_addresses = []

cd          = os.path.dirname(__file__)
accs        = os.path.join(cd, '../info/account_list.txt')
sealer_accs = os.path.join(cd, '../info/sealer_account_list.txt')
enode_path  = os.path.join(cd, '../info/enode.txt')
pwd_path    = os.path.join(cd, '../info/password.txt')

enode = ''
with open(enode_path) as key:
    enode = key.readline()
enode = enode[:len(enode)-1]

with open(sealer_accs) as sealer_acc_list:
    line = 'not empty'
    while len(line) > 0:
        line = sealer_acc_list.readline()
        if not len(line) == 0 and line[0] == '0':
            sealer_addresses.append(line[:len(line)-1])

with open(accs) as acc_list:
    line = 'not empty'
    while len(line) > 0:
        line = acc_list.readline()
        if not len(line) == 0 and line[0] == '0':
            node_addresses.append(line[:len(line)-1])


node_processes = []

i = 1
for address in node_addresses:
    dir = os.path.join(cd, '../nodes/node' + str(i) + '/')
    port = 30310 + i
    rpcport = 8500 + i

    c = 'geth '
    c += '--datadir ' + str(dir) + ' '
    c += '--syncmode \"full\" '
    c += '--port ' + str(port) + ' '
    c += '--rpc '
    c += '--rpcaddr \"localhost\" '
    c += '--rpcport ' + str(rpcport) + ' '
    c += '--rpcapi \'personal,eth,net,web3,txpool,miner\' '
    c += '--bootnodes \"' + enode + '\" '
    c += '--networkid 1515 '
    c += '--gasprice 1 '
    c += '-unlock \"' + address + '\" '
    c += '--password ' + pwd_path + ' '
    c += '--allow-insecure-unlock '
    c += '--ipcdisable '
    c += '--verbosity 3'

    node_processes.append(start(c))
    print('Started node ' + str(i))

    i+=1

i = 1
for address in sealer_addresses:
    dir = os.path.join(cd, '../nodes/sealer' + str(i) + '/')
    port = 30360 + i
    rpcport = 8550 + i

    c = 'geth '
    c += '--datadir ' + str(dir) + ' '
    c += '--syncmode \"full\" '
    c += '--port ' + str(port) + ' '
    c += '--rpc '
    c += '--rpcaddr \"localhost\" '
    c += '--rpcport ' + str(rpcport) + ' '
    c += '--rpcapi \'personal,eth,net,web3,txpool,miner\' '
    c += '--bootnodes \"' + enode + '\" '
    c += '--networkid 1515 '
    c += '--gasprice 1 '
    c += '-unlock \"' + address + '\" '
    c += '--password ' + pwd_path + ' '
    c += '--mine '
    c += '--allow-insecure-unlock '
    c += '--ipcdisable '
    c += '--verbosity 3'

    node_processes.append(start(c))    
    print('Started sealer ' + str(i))

    i+=1