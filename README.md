# Smart-Contract-AV-Volume-Reservation
Using a smart contract deployed on a private Ethereum blockchain to simulate how volume reservation by autonomous vehicles would work, including V2V exchange of volumes.

# Tools used
* Windows 10 Pro, version 1903, build 18362.657
* Geth & Tools 1.9.11 64-bit https://geth.ethereum.org/downloads/
* Visual Studio Community 2019
* Python 3.7
* Git Bash (MINGW64)

# Setup from scratch
* Delete everything but the .bat files, .py files and password.txt
* Git Bash in root/network
* Run createsealers.bat (will create 3 folders).
* Run createaccounts.bat (will create 50 folders).
* Run puppeth.
* answer network, 2, 1, 2, 5, <sealer node addresses from sealer_account_list.txt (every other line without '0x', [ENTER] between each, [ENTER] without address to finish)>, [ENTER], no, 1515, 2, 2, genesis 
* Run prefund_accounts_in_json.py (modifies genesis file with prefunding for each of the 53 accounts to save you from doing it manually).
* Run initsealers.bat
* Run initaccounts.bat
* Run startnodes.py

