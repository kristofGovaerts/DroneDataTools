# -*- coding: utf-8 -*-
"""
Author: Kristof Govaerts

Select a folder containing .dbf files (global variable EXT). This script then 
browses all of these files, looking for different parameters (global variable PARS).
It then checks if there are multiple files for each parameter, concatenating
into a single .csv file for each parameter, adding an extra column for each date.
"""

import simpledbf
import pandas as pd
import glob
import os
from tkinter import filedialog
from tkinter import Tk
from datetime import datetime
from functools import reduce #standard in python 2.x, not in 3

root = Tk()
root.withdraw()

WDIR = filedialog.askdirectory()
EXT = '.dbf'
#PARS = ['cover', 'ndre', 'ndvi', 'osavi', 'plantheight', 'psri']
#PARS = ['band1','band2','band3','band4','band5']
PARS = ['cover', 'coverMS', 'ndre', 'ndvi', 'osavi', 'plantheight', 'psri', 
        'tdvi', 'tdvi_masked', 'cigreen', 'cirededge', 'mcari']
#JOIN_ON = ['X','Y', 'fieldcode', 'time', 'date']
JOIN_ON = ['X','Y', 'time', 'date'] #list of parameters to use for joining dataframes
DATEFORM = 'YYYYMMDD'
DATEMIN = datetime(2019, 6, 4)
REP = 'G01'
OUT_FILENAME = 'combined_pars.csv'

os.chdir(WDIR)

filelist = glob.glob('*' + EXT)

def get_dates_from_filenames(l):
    els = [f.split('_') for f in outlist] #list of  all elements in filenames (separarator = _)
    uels = list(set([j for i in els for j in i])) #unique elements
    out = [e for e in uels if e.isdigit() and len(e)==8]
    return out

dflist_all=[]
for par in PARS:
    outlist = [f for f in filelist if '_' + par + '.' in f]
    if len(outlist) == 0:
        print("Parameter {} not found.".format(par))
        continue
    dates = get_dates_from_filenames(outlist)
    print("Parameter: {}\nFound {} dates: {}".format(par, len(dates), dates))
        
    dflist = []
    for date in dates:
        infile = list(filter(lambda x: date in x, outlist)) #python 3 requires conversion from filter to list 
        if len(infile) == 1: #make sure there is only one file for each date
            infile = infile[0]
        else: #this condition should not occur. If necessary an exception can be added here
            print('Error: Multiple files found for date {}.'.format(date))
            break
        df = simpledbf.Dbf5(infile).to_dataframe()
        df['date'] = date
        
        if DATEFORM == 'YYYYMMDD':
            time = datetime(int(date[0:4]), int(date[4:6]), int(date[6:])) - DATEMIN
            df['time'] = time.days
        df = df.dropna(axis=1, how='all') #remove empty columns
        dflist.append(df)
    out_df = pd.concat(dflist)
    out_df.columns = [c.replace(REP, par) for c in out_df.columns]
    dflist_all.append(out_df)

finaldf = reduce(lambda x, y: pd.merge(x, y, on = JOIN_ON, how='outer'), dflist_all)
print("Timepoints (minimum should be 0):")
print(set(finaldf['time']))
finaldf.to_csv(path_or_buf=OUT_FILENAME, sep='\t')