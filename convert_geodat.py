
# forked from Daniel Shapiro
# simplifying to a simple ian file reader 

import numpy as np
from scipy.io import *
import struct
import sys
import math
import pylab as plt
from idw import fill_missing_data

import rasterio


def read_geodat(filename):
    """
    Read in one of Ian's geodat files.

    Parameters:
    ==========
    filename: the name of the geodat file to read; expects that there is
              also a file called "filename.geodat", which contains info
              on grid size, spacing, etc.

    Returns:
    =======
    x, y: the grid coordinates of the output field
    data: output field
    """

    def _read_geodat(filename):
        # read in the .geodat file, which stores the number of pixels,
        # the pixel size and the location of the lower left corner
        geodatfile = open(filename, "r")
        xgeo = np.zeros((3, 2))
        i = 0
        while True:
            line = geodatfile.readline().split()
            if len(line) == 2:
                try:
                    xgeo[i, 0] = float(line[0])
                    xgeo[i, 1] = float(line[1])
                    i += 1
                except ValueError:
                    i = i
            if len(line) == 0:
                break
        geodatfile.close()
        xgeo[2, :] = xgeo[2, :] * 1000.0
        return xgeo

    # Get the data about the grid from the .geodat file
    xgeo = _read_geodat(filename + ".geodat")
    nx, ny = map(int, xgeo[0,:])
    dx, dy = xgeo[1, :]
    xo, yo = xgeo[2, :]

    x = np.zeros(nx)
    for i in range(nx):
        x[i] = xo + i * dx

    y = np.zeros(ny)
    for i in range(ny):
        y[i] = yo + i * dy

    # Open the x-velocity file and read in all the binary data
    data_file = open(filename, "rb")
    raw_data = data_file.read()
    data_file.close()

    # Unpack the binary data to an array of floats, knowing that it is
    # in big-endian format.
    nvals = len(raw_data)/4
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f', raw_data[4*i: 4*(i+1)])[0]

    # Reshape the 1D array to 2D
    data = arr.reshape((ny, nx))

    # Fill in any small patches of missing data
    #data = fill_missing_data(data, -2.0e+9)

    return x, y, data

def numpyGeoTiff(numpyarray,filename,originalTiff):
    """
    Turn a numpy array into a geoTiff

    Parameters:
    ==========
    numpyarray: the 2-d numpy array
    
    fileName: the name you want 
    
    originalTiff: this is the kicker. You need to give it a proper geoTiff for
                for it it emulate

    Returns:
    =======
    nothing, but it dumps a tif into the file path you gave it.  
    """
    
    # open the original geotiff 
    r = rasterio.open(originalTiff)
    
    # get its profile info    
    profile = r.profile
    
    # udate to the correct 
    profile.update(dtype=rasterio.float64,
                   count=1,
                   nodata=-2.0e+9)
    
    with rasterio.open(filename+"_new.tif", 'w', **profile) as dst:
        
        # update the metadata/ the geo part of the geotif
        #kwargs = dst.meta
        #kwargs.update(
        #        dtype=rasterio.float64,
        #        count=1)
        
        # now write the data. 
        dst.write(numpyarray, 1)
        
    return profile

def warpRasterToRaster(rasterToChange,rasterToMatch,outputFileName):
    """
    Turn a numpy array into a geoTiff

    Parameters:
    ==========
    rasterToChange: the file you want to regrid/warp
    
    rasterToMatch: the file that you want the warped image to match
    
    outputFileName: the name of the output file this function will create

    Returns:
    =======
    nothing, but it dumps a tif into the file path you gave it.  
    """
     
    # this is from stack overflow 
    # http://stackoverflow.com/questions/10454316/how-to-project-and-resample-a-grid-to-match-another-grid-with-gdal-python
     
    from osgeo import gdal, gdalconst

    # Source

    src = gdal.Open(rasterToChange, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    src_geotrans = src.GetGeoTransform()
    
    # We want a section of source that matches this:
    
    match_ds = gdal.Open(rasterToMatch, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize
    
    # Output / destination
    dst = gdal.GetDriverByName('GTiff').Create(outputFileName, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)
    
    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Bilinear)
    
    del dst # Flush

# ===================================================================
# ===================================================================
# start the main body of Code 
# ===================================================================
# ===================================================================

# file to convert 
pathName = "X:\\Track-All250\\"
filename_y = pathName +"mosaicOffsets.vy"
filename_x = pathName +"mosaicOffsets.vx"

# pointing this at ians qualitiative picture tif.    
originalTiff = "X:\\Track-All250\\velocity.tif"  

# x component

xx,yx,datax = read_geodat(filename_x)

dataFlipX = np.flipud(datax)

numpyGeoTiff(dataFlipX,filename_x,originalTiff)

# y component

xy,yy,datay = read_geodat(filename_y)

dataFlipY = np.flipud(datay)

numpyGeoTiff(dataFlipY,filename_y,originalTiff)


# vector magnitude 
# good old trig 
# a**2 + b** = c**2 

dataFlip_magnitude = np.sqrt(dataFlipY**2 + dataFlipX**2)

# re- set the no data values to no data 
dataFlip_magnitude[dataFlipY == -2.0e+9] = -2.0e+9

numpyGeoTiff(dataFlip_magnitude,pathName+"Magnitude",originalTiff)


# now use gdal warp to match the gridding of each file 
# warpRasterToRaster(rasterToChange,rasterToMatch,outputFileName):

basalShearTif = "Y:\\Documents\\DATA\\MORLIGHEM_NSIDC\\basal_shear_Pa_Layer.tif"

# this warps the velocity to match the basal shear layer 
warpRasterToRaster(pathName+"Magnitude"+"_new.tif",basalShearTif,pathName+"testReGrid.tif")