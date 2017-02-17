import os
import csv
import datetime
import getopt
import sys
import json
from threading import Thread
import time

#v1 Initial Release
#v2 Update to Search for GVNs

class findgame():

    def parseMID(self, mid):
        manufacturer = ''
        if (mid == '00'): manufacturer = 'Aristocrat'
        elif (mid == '01'): manufacturer = 'IGT'
        elif (mid == '05'): manufacturer = 'Aruze'
        elif (mid == '07'): manufacturer = 'SG Gaming'
        elif (mid == '09'): manufacturer = 'Konami'
        elif (mid == '12'): manufacturer = 'AGT'
        else: manufacturer = mid

        return manufacturer

    def read_datafile_multi_items(self, filename, dffieldnames, df_id):
        resultlist = list()
        with open(os.path.join(self.pathtodatafiles, filename),'r') as datafile:
            reader = csv.DictReader(datafile, delimiter=',',fieldnames=dffieldnames)

            if self.gamename_flag: # Searching for Game Names
                for row in reader:
                    if (row['software_set_name'].find(df_id.upper(), 0, len(row['software_set_name'])) != -1):
                        resultlist.append(row)
            if self.gvn_flag: # Searching for GVN
                for row in reader:
                    if (row['version_number'].find(df_id.upper(), 0, len(row['version_number'])) != -1):
                        resultlist.append(row)

        return (resultlist)
    
    def ReadDatafiles_gamename(self):
        gamelist = list()
        gamelist = self.read_datafile_multi_items(self.datafile, self.ss1fieldnames, self.tmp_gamename)
        games = []
        
        if (len(gamelist) > 0):
            for row in gamelist:
                output_mid = self.parseMID(row['mid'])
                output_App_Date = str(datetime.datetime.strptime(row['appdate'], "%Y%m%d").date())
                games.append(json.dumps(dict(Manufacturer=output_mid, Game_Info=row['software_set_name'].rstrip(),
                                  SSAN=row['ssan'], Approval_Date=output_App_Date), indent=4, sort_keys=True, separators=(',',':')))
        else:
            print("No game name found with string: " + self.tmp_gamename)
            sys.exit(0)

        return games

    def ReadDatafiles_gvn(self):
        gamelist = list()
        gamelist = self.read_datafile_multi_items(self.datafile, self.sg0fieldnames, self.gvn)
        games = []

        if (len(gamelist) > 0):
            for row in gamelist:
                output_mid = self.parseMID(row['mid'])
                games.append(json.dumps(dict(Manufacturer=output_mid, SSAN=row['ssan'],
                                             Game_Name=self.getGameName(row['ssan']),
                                             GVN=row['version_number'], VAR=row['var'],
                                             RTP=row['rtp']), indent=4, sort_keys=True, separators=(',',':')))
        else:
            print("No GVN found : " + self.gvn)
            sys.exit(0)
        return games            

    def getdatafile_filenames(self, datafiles, ftype):
        for item in datafiles:
            # time.sleep(100)
            if item.upper().endswith(ftype): self.datafile = item

        if self.datafile == '':
            print("Expected directory containing " + ftype + " file. Check Directory")
            sys.exit(2)

    def getGameName(self, ssan):
        gamename = ''
        resultlist = list()
        datafiles = os.listdir(self.pathtodatafiles)
        Thread(target=self.getdatafile_filenames(datafiles, "SS1")).start() # SS1 file contains game name

        with open(os.path.join(self.pathtodatafiles, self.datafile),'r') as datafile:
            reader = csv.DictReader(datafile, delimiter=',',fieldnames=self.ss1fieldnames)
            for row in reader:
                if (row['ssan'].upper() == ssan.upper()):
                        resultlist.append(row['software_set_name'].rstrip()) # just game name
                        # resultlist.append(row) # will show all game details in SS1 file
        return (resultlist)        

    def __init__(self):
        DEFAULT_DF_LOCATION = "S:\cogsp\docs\data_req\download"
        self.ss1datafile = ''
        self.pathtodatafiles = ''
        self.df_filetype = ''
        self.gamename_flag = False
        self.dffile_flag = False
        self.manualpath = False
        self.gvn_flag = False
        self.ss1fieldnames = ['mid','software_set_name','software_set_id','ssan','protocolv','status','man_ver_id','appdate','market','denom']
        self.sg0fieldnames = ['mid','software_component_id','ssan','version_number','var','rtp','status','market']
        self.tmp_gamename = ''
        self.gvn = ''
        
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'g:d:v:h',['game=','datafiles=','version=','help'])
            
            for opt, arg in opts:
                if opt == '-h':
                    print('Usage: findgame.py --game <game name> --datafiles <path to datafiles> --version <GVN>')
                    print('    where: ')
                    print('           --game or -g       game name to find SSAN')
                    print('           --version or -v    game name to find GVN')
                    print('           --datafiles or -d  Directory of Datafiles')
                    print('                              if option -d is not provided will default to:   ')
                    print('                                - ' + DEFAULT_DF_LOCATION)
                    sys.exit()
                elif opt in ("-g", "--game"):
                    self.gamename_flag = True
                    self.tmp_gamename = arg
                elif opt in ("-d", "--datafiles"):
                    self.pathtodatafiles = arg
                    self.manualpath = True
                elif opt in ("-v", "--version"):
                    self.gvn_flag = True
                    self.gvn = arg

            # Get path to datafiles based on args
            if (self.manualpath == False):
                self.pathtodatafiles = DEFAULT_DF_LOCATION
                
            print("Using datafiles from: " + self.pathtodatafiles)

            if self.gamename_flag: 
                if os.path.isdir(self.pathtodatafiles):                    
                    datafiles = os.listdir(self.pathtodatafiles)
                    Thread(target=self.getdatafile_filenames(datafiles, "SS1")).start() # SS1 file contains game name
                    for item in self.ReadDatafiles_gamename():
                        print(item)
                else:
                    print("Expected path to datafiles, got: " + self.pathtodatafiles)
                    sys.exit(2)
            
            if self.gvn_flag:
                print("Looking for GVN: " + self.gvn)
                if os.path.isdir(self.pathtodatafiles):                    
                    datafiles = os.listdir(self.pathtodatafiles)
                    Thread(target=self.getdatafile_filenames(datafiles, "SG0")).start() # SGO file contains GVN info
                    for item in self.ReadDatafiles_gvn():
                        print(item)
                else:
                    print("Expected path to datafiles, got: " + self.pathtodatafiles)
                    sys.exit(2)

            # catch all
            if not self.gvn_flag and not self.game_name_flag: 
                print("check flags, didn't get -g or --game")
                sys.exit(2)
                
        except getopt.GetoptError:
            print("try: findgame.py -h for more info")
            sys.exit(2)

def main():   
    if (len(sys.argv) < 2):
        print('not enough parameters passed, try option -h for more info.')
        sys.exit(2)
    else: 
        app  = findgame()

if __name__ == "__main__": main()
