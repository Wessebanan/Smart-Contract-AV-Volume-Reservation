@echo off
bootnode -genkey %~dp0../info/boot.key
bootnode -nodekey %~dp0../info/boot.key -verbosity 9 -addr :30310 > %~dp0../info/enode.txt