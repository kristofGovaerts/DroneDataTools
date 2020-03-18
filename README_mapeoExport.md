# mapEO import / export & data pre-processing
#### *17/03/2020*

This guide outlines how to **add field layouts to mapEO** and subsequently **export data from mapEO**, before converting to tabular (.csv) format with X/Y coordinates, date/time info, and seperate columns for each measured column.

## Step 1. mapEO import / export

1. **Upload shape files containing the **plot layout** to mapEO**

   1.1. Export the plot layout from QGis (see also the general **README** for documentation on how to generate plots from scratch 
   or from .kml files in QGis). The layer of interest should be exported as an *ESRI Shapefile*, using *UTF-8 encoding* and (important)
   the *EPSG:4326 - WGS 84* coordinate reference system (CRS). 

   1.2. Add all components of the ESRI shapefile to a **.zip** (QGis-generated ESRI shapefiles consist of .cpg, .dbf, .prj, .qpj, .shp 
   and .shx files).

   1.3. Open **mapEO**, log in, and select the field of interest.

   1.4. Click **Field Layout**. Click **ADD** to add a field layer. You can generate a seperate layer for each type of delineation 
   (ex: different plot sizes)

   1.5. Click **IMPORT** and load the .zip file generated in step 1.2..

2. **Export **plot statistics** from mapEO**

   2.1. Under **Field Layout**, activate the layer of interest (ex: Layer 1).
   
   2.2. Scroll down to **EXPORT** and click the slider if this box is not open.
   
   2.3. Click **FIELD DATA**
   
   2.4. Click **ALL FIELDS** (unless you only need a subset of data)
   
   2.5. Select **Shapefile** 
   
   2.6. Select **Parameters to export** (ex. ndvi, cover)
   
   2.7. Select **Dates / timepoints to export**
   
   2.8. Enter your e-mail address and click **EXPORT**.
   
   2.9. Files should arrive within one minute.

## Step 2. Compile exported files into a single .csv

Run **shpZip_to_csv.py**. Select the .zip containing the shapefiles exported from mapEO. Normally, no edits will need to be made to the code. However, extracted columns can be added or removed by editing the COLS variable. The output will be a **tab-delimited .csv** with the following columns:
   * X, Y: X and Y coords
   * time: Time in days after the earliest timepoint found. Lowest should be 0.
   * date: The date, formatted as a string.
   * *(n_pars * n_cols)* columns. One column for each parameter specified in global variable COLS (default mean, median, min, max, stddev), and one column for each parameter (eg ndvi, cover, ndre, ... ). 
