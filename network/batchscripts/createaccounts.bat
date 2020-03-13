@echo off
FOR /L %%A IN (1,1,10) DO (
    mkdir %~dp0../nodes/node%%A
    geth --datadir %~dp0../nodes/node%%A --password %~dp0../info/password.txt account new | sed -n -e 's/^.*: //p'| sed 's/ //g' >> %~dp0../info/account_list.txt
)
