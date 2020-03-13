import os
import json

cd = os.path.dirname(__file__)
accs = os.path.join(cd, '../info/account_list.txt')
sealer_accs = os.path.join(cd, '../info/sealer_account_list.txt')

genesis = os.path.join(cd, '../nodes/genesis/network.json')

prefund_addresses = []

with open(sealer_accs) as sealer_acc_list:
    line = 'not empty'
    while len(line) > 0:
        line = sealer_acc_list.readline()
        if not len(line) == 0 and line[0] == '0':
            prefund_addresses.append(line[2:len(line)-1])

with open(accs) as acc_list:
    line = 'not empty'
    while len(line) > 0:
        line = acc_list.readline()
        if not len(line) == 0 and line[0] == '0':
            prefund_addresses.append(line[2:len(line)-1])


f = open(genesis, "r")
contents = f.read()
f.close()

decoder = json.JSONDecoder()

decoded_json = decoder.decode(contents)
for address in prefund_addresses:
    decoded_json['alloc'][address] = {'balance': '0x200000000000000000000000000000000000000000000000000000000000000'}

encoder = json.JSONEncoder(indent=2)

encoded_json = encoder.encode(decoded_json)

f = open(genesis, "w")
encoded_json = "".join(encoded_json)
f.write(encoded_json)
f.close()