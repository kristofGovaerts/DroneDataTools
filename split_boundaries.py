# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 09:30:02 2019

@author: Govaerts.Kristof

Works with exported csv files from QGIS with the following settings:
    Format - CSV
    Geometry: Geometry type - Polygon
    Layer options: GEOMETRY  - AS_WKT
                   SEPARATOR - SEMICOLON
    Note that the polygon points may have to be in the correct order. This 
    order is: 
        Top left, top right, bottom right, bottom left, top left 
        (assuming polygons are to be splitted along top/down axis)
"""

from tkinter import filedialog
from tkinter import Tk
import pandas as pd
import numpy as np

#global vars
PLOTS_COL = "plots"
X0 = "X0" #The column containing the first X coordinate from which others are calculated
Y = "Y" 
POL = "WKT"
SEP = ';' #separator for csv files
OUT = 'WKT' #output file format: well known text: eg "POLYGON((x1 y1,x2 y2,x3 y3,x4 y4,x1 y1))"
SPLIT_AXIS = 1 #0 or 1

RESIZE = True
RESIZE_X = 0.0 #ALong which axis to split. If buffering plots, Y is correct
RESIZE_Y = 0.1

root = Tk()
fn =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
root.withdraw()

print('File: ' + fn)

f = pd.read_csv(fn, sep=SEP)
print('\nData frame shape: ' + str(f.shape))

def dist(p1, p2): #distance between two pts in 2D space
    d = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return d

def wkt_to_pol(wkt): #convert well known text to polygon in np array
    t = wkt[wkt.find("(")+1:wkt.find(")")]
    t = t.replace('(', '').replace(')','')
    pts = np.array([c.split(' ') for c in t.split(',')]).astype('float')
    return pts

def pol_to_wkt(pol): #convert polygon to well known text
    p = 'POLYGON(('
    for c in range(5):
        p += str(pol[c,0]) + ' ' + str(pol[c,1]) 
        if c<4:
            p += ','
    p += '))'
    return p
        
def generate_pt(p1, p2, where): #generate point on line between p1 and p2, on certain distance from p1
    d = dist(p1, p2)
    n = d-where
    r = n/d
    p1n = ((1-r)*p2[0] + r*p1[0], (1-r)*p2[1] + r*p1[1])
    return(p1n)
    
def split_pol(pol, ax, n):
    print("Axis 1 length: " + str(dist(pol[0,:], pol[1,:])))
    print("Axis 2 length: " + str(dist(pol[1,:], pol[2,:])))
    print("Splitting along axis " + str(ax+1) + " into " + str(n) + " plots.")
    d = dist(pol[ax,:], pol[ax+1,:])
    s = d/n
    a = (pol[ax,:], pol[ax+1,:]) #list of boundary pts on one side
    b = (pol[-((1-ax)+2),:], pol[-((1-ax)+1),:]) #list of pts on other side
    
    outlist = []
    for i in range(n):
        npol = np.array([generate_pt(a[0], a[1], s*i),
                         generate_pt(a[0], a[1], s*(i+1)),
                         generate_pt(b[1], b[0], s*(i+1)),
                         generate_pt(b[1], b[0], s*i),
                         generate_pt(a[0], a[1], s*i)])
        outlist.append(pol_to_wkt(npol))
    return outlist

def resize(p1, p2, by):
    d = dist(p1, p2)
    n = d-by #new length
    r = n/d
    
    p1n = ((1-r)*p2[0] + r*p1[0], (1-r)*p2[1] + r*p1[1])
    p2n = ((1-r)*p1[0] + r*p2[0], (1-r)*p1[1] + r*p2[1])
    return(p1n, p2n)
        
def resize_pol(pol, x, y):
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

ndf = pd.DataFrame(columns=['POL', 'X', 'Y'])
for i in range(len(f)):
    n =  f[PLOTS_COL][i] 
    xstart = f[X0][i]
    
    pols = split_pol(wkt_to_pol(f[POL][i]), SPLIT_AXIS, n)
    x = [xstart + j for j in range(n)]
    y = [int(f[Y][i]) for j in range(n)]
    
    cdf = pd.DataFrame()
    cdf['POL'] = pols
    cdf['X'] = x
    cdf['Y'] = y
    ndf = pd.concat([ndf, cdf])

if RESIZE:
    pols = list(ndf['POL'])
    print("Resizing. Factors:")
    print("X: " + str(RESIZE_X))
    print("Y: " + str(RESIZE_Y))
    pols2 = [pol_to_wkt(resize_pol(wkt_to_pol(p), RESIZE_X, RESIZE_Y)) for p in pols]
    ndf['POL'] = pols2

ndf.to_csv(fn.replace('.csv', '_splitted.csv'),sep=';')