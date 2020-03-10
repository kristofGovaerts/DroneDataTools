# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 09:30:02 2019

@author: Govaerts.Kristof

Works with ; delimited .csv files with one column for each corner point of a rectangular polygon.
"""

from tkinter import filedialog
from tkinter import Tk
import pandas as pd
import numpy as np

#global vars
X = ('ULX', 'URX', 'ORX', 'OLX') #name of cols with X coords, in order
Y = ('ULY', 'URY', 'ORY', 'OLY') #name of cols with Y coords, in order
SEP = ';' #separator for csv files
OUT = 'WKT' #output file format: well known text: eg "POLYGON((x1 y1,x2 y2,x3 y3,x4 y4,x1 y1))"

RESIZE = True
RESIZE_X = 5e-6
RESIZE_Y = 2.5e-6

root = Tk()
fn =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
root.withdraw()

print('File: ' + fn)
print('\nColumn names: Edit global vars if incorrect' )
print('\nX columns: ' + str(X) + '\nY columns: ' + str(Y) )

f = pd.read_csv(fn, sep=SEP)
print('\nData frame shape: ' + str(f.shape))

def dist(p1, p2):
    d = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return d

def wkt_to_pol(wkt):
    t = wkt[9:-2]
    pts = np.array([c.split(' ') for c in t.split(',')]).astype('float')
    return pts

def pol_to_wkt(pol):
    p = 'POLYGON(('
    for c in range(5):
        p += str(pol[c,0]) + ' ' + str(pol[c,1]) 
        if c<4:
            p += ','
    p += '))'
    return p

def resize(p1, p2, by): #Given two points, resizes around center between said points.
    d = dist(p1, p2)
    n = d-by #new length
    r = n/d
    
    p1n = ((1-r)*p2[0] + r*p1[0], (1-r)*p2[1] + r*p1[1])
    p2n = ((1-r)*p1[0] + r*p2[0], (1-r)*p1[1] + r*p2[1])
    return(p1n, p2n)
        
def resize_pol(pol, x, y): #Given a polygon, resizes using X and Y. 
    #side lengths
    d1 = dist(pol[0,:], pol[1,:])
    d2 = dist(pol[1,:], pol[2,:])
    d3 = dist(pol[2,:], pol[3,:])
    d4 = dist(pol[3,:], pol[4,:])

    if d1+d3 < d2+d4: #determine which axis is width and which is height
        w = 1
    else:
        w = 0
    
    out = np.zeros(pol.shape)
    
    #resize width
    out[0:2,:] = np.array(resize(pol[w,:], pol[w+1,:], x))
    out[2:4,:] = np.array(resize(pol[w+2,:], pol[w+3,:], x))
    out[-1,:] = out[0,:]
    
    #resize height
    out[1:3,:] = np.array(resize(out[1,:], out[2,:], y))
    out[3:5,:] = np.array(resize(out[3,:], out[4,:], y))    
    out[0,:] = out[-1,:]
    
    return out    

pols =  [] #empty list for polygons
for i in range(len(f)):
    p = "POLYGON(("
    for c in range(4):
        p += (str(f[X[c]][i]) + ' ' + str(f[Y[c]][i]) + ',')
    p += (str(f[X[0]][i]) + ' ' + str(f[Y[0]][i]) + '))') #add start pt
        
    if RESIZE:
        print("Resizing. Factors:")
        print("X: " + str(RESIZE_X))
        print("Y: " + str(RESIZE_Y))
        p = resize_pol(wkt_to_pol(p), RESIZE_X, RESIZE_Y)
        p = pol_to_wkt(p)     
    pols.append(p)
f['POL'] = pols

f.to_csv(fn.replace('.csv', '_pols.csv'),sep=';')