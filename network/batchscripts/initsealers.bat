@echo off
FOR /L %%A IN (1,1,3) DO (
	geth --datadir  %~dp0../nodes/sealer%%A/ init  %~dp0../nodes/genesis/network.json
)