# DroneDataTools
Python tools for compiling incoming drone data. Several .py files are available for different purposes.

## collect_dbf_files_tosingle.py
This tool scans a folder containing multiple .dbf files which are specifically formatted. Such .dbf files should contain the **date** and the **parameter type** (i.e. NDVI, Cover, etc) in their filename, as well as an **X** and **Y** spatial column. The output is a 2D .csv file containing columns for **time**, **X**, **Y**, **date**, followed by columns extracted from each parameter file. 

The purpose of this script is to provide a single file which is easily read into R for further statistical processing.

## split_boundaries.py
This tool takes a .csv shapefile generated from QGis and splits the polygons defined inside according to predefined rules, for the semi-automatic delineation of plots for agricultural data. The intended use is as follows:

1. Outline the boundaries of different field blocks. Such boundaries should be rectangular, and several parameters should be defined in QGis:

  * *plots*  The amount of plots in the delineated block. 
  * *Y* The Y-coordinate of the block, i.e. the column number. 
  * *fieldcode* The X and Y coordinates of the first plot in the block. Formatted with a space in between, eg for plot X1Y1 = *1 1*

2. Export as .csv. Precise requirements: 
  *Format - CSV
  *Geometry: Geometry type - Polygon
  *Layer options: GEOMETRY  - AS_WKT, SEPARATOR - SEMICOLON
  
3. Define options in .py file if necessary. Particularly, you may need to adjust RESIZE_X and RESIZE_Y to add a buffer between plots.

4. Run .py file. Select the .csv boundary file, which will be scanned and splitted. Output is saved as *boundaries_splitted.csv*. This file can be re-imported into QGis. 

## pts_to_pol.py
This script is meant to format miniGIS files into discrete polygons based on the point coordinates in the file. 

