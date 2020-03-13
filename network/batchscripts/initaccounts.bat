@echo off
FOR /L %%A IN (1,1,10) DO (
	geth --datadir %~dp0../nodes/node%%A/ init  %~dp0../nodes/genesis/network.json
)