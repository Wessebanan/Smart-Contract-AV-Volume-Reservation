::@echo off
FOR /L %%A IN (1,1,3) DO (
    mkdir sealer%%A
    geth --datadir node%%A/ --password password.txt account new | sed -n -e 's/^.*: //p'| sed 's/ //g' >> account_list.txt
    geth --datadir node%%A/ init genesis/devnet.json
)
