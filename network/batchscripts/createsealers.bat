@echo off
FOR /L %%A IN (1,1,3) DO (
    mkdir %~dp0../nodes/sealer%%A
    geth --datadir %~dp0../nodes/sealer%%A --password %~dp0../info/password.txt account new | sed -n -e 's/^.*: //p'| sed 's/ //g' >> %~dp0../info/sealer_account_list.txt
)
