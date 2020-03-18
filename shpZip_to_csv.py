# -*- coding: utf-8 -*-
"""
Author: Kristof Govaerts

Select a .zip file. This zip file must contain one subfolder for each parameter
and each timepoint, and each subfolder should contain one shapefile (specifically,
the .dbf component of the shapefile).

This script then browses all of these files, looking for different parameters (like ndvi, ndre,...)
It then checks if there are multiple files for each parameter, concatenating
into a single .csv file for each parameter, adding an extra column for each date. 
Another column is added for time, with the earliest timepoint set to 0.
"""

import zipfile
import simpledbf
import pandas as pd
import os, shutil
import re
from tkinter import filedialog
from tkinter import Tk
from datetime import datetime
from functools import reduce #standard in python 2.x, not in 3

JOIN_ON = ['X','Y', 'time', 'date'] #by which columns to join. 
COLS = ['minimum', 'maximum', 'mean', 'median', 'stddev'] #which columns to export
POLFILE = 'polygon.dbf' #exact filename of the polygon .dbf file inside the subfolder
DATEFORM = '%Y%m%d' #date format - for extracting timepoints. Default recommended, otherwise length 8

if DATEFORM == '%Y%m%d':
    DPAT = '20\d{6}' #pattern for searching dates. Year will start with 20 for at least 80 more years
else:
    DPAT = '\d{8}' #Less specific

root = Tk()
root.withdraw()

ZIP = filedialog.askopenfilename()
os.chdir(os.path.split(ZIP)[0]) #set working dir
tdir = 'temporary'  #extract to folder named temporary, to delete later
with zipfile.ZipFile(ZIP, 'r') as zipObj:
   zipObj.extractall(tdir)
   
subf = [os.path.join(tdir, o) for o in os.listdir(tdir) 
                    if os.path.isdir(os.path.join(tdir,o))]

pars = list(set([sf.split('_')[-1] for sf in subf])) #unique parameters
dates = list(set([re.findall(DPAT, sf)[0] for sf in subf])) #unique dates
dates_dt = [datetime.strptime(d, DATEFORM) for d in dates]
DATEMIN = min(dates_dt)
OUT_FILE = os.path.split(ZIP)[1].replace('.zip', '_all.csv')

print("""
Unique parameters found:\n {}

Unique dates found:\n {}

First timepoint:\n {}

Output file: \n {}
-------------------------------------------------------------------------------

Compiling...
""".format(pars, dates, DATEMIN, os.path.join(os.getcwd(), OUT_FILE)))

dflist_all=[] #output list

for par in pars:
    outlist = [f for f in subf if '_' + par in f]
    if len(outlist) == 0:
        print("Parameter {} not found.".format(par))
        continue
    print('Parameter {}: {} dates found.'.format(par, len(outlist)))
        
    dflist = []
    
    for i, date in enumerate(dates):
        infol = list(filter(lambda x: date in x, outlist)) #python 3 requires conversion from filter to list 
        if len(infol) == 1: #make sure there is only one file for each date
            infol = infol[0]
        else: #this condition should not occur. If necessary an exception can be added here
            print('Error: Multiple files found for date {}.'.format(date))
            break
        
        df = simpledbf.Dbf5(os.path.join(infol, POLFILE)).to_dataframe()
        df['date'] = date
        df['time'] = (dates_dt[i] - DATEMIN).days
        df = df.dropna(axis=1, how='all') #remove empty columns
        dflist.append(df)
        
    out_df = pd.concat(dflist) #vertical concatenation
    out_df = out_df[['X', 'Y', 'time', 'date'] + COLS] #trim
    out_df.columns = [par + '_' + col if col in COLS else col for col in out_df.columns]
    dflist_all.append(out_df)

finaldf = reduce(lambda x, y: pd.merge(x, y, on = JOIN_ON, how='outer'), dflist_all)
print("\nTimepoints in final dataframe (minimum should be 0):\n {}".format(list(set(finaldf['time']))))

finaldf.to_csv(path_or_buf=OUT_FILE, sep='\t')

shutil.rmtree(os.path.join(os.getcwd(), tdir)) #clean up