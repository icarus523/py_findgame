# py_findgame

This is a script to be used with OLGR's datafiles to find a game's:  

* Approval Number (SSAN) or  
* GVN (Game Variation Number)  

## OLGR datafiles 
Refer to [https://publications.qld.gov.au/dataset/data-requirements-for-monitored-gaming-machines]

Ideally this is a script to be used with the DatafilesBrowser.py script, which will help you find the game you need information for without the use of COGS (Corporate Office Gaming System) Database.  

## How to Use

### Find game via GVN
> py findgame.py -v <GVN>

### Find game via game name
> py findgame.py -g <"GAME NAME">

