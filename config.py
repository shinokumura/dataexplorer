import os

DEVENV = True

if DEVENV:
    DATA_ROOT_FOLDER = "/Users/okumuras/Documents/nucleardata/libraries/"
    MT_PATH  = "datahandle/MT.dat"
    
else:
    DATA_ROOT_FOLDER = "/srv/data/dataexplorer/"
    MT_PATH  = "/srv/www/exforpyplot/datahandle/MT.dat"


LIB_PATH = os.path.join(DATA_ROOT_FOLDER, "libraries/")
EXP_PATH = os.path.join(DATA_ROOT_FOLDER, "libraries/")

# for FY
LIB_PATH_FY = os.path.join(LIB_PATH, "FY/")
EXP_PATH_FY = os.path.join(LIB_PATH, "FY/")
