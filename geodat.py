import numpy as np
from scipy.io import *
import struct
import sys
import math

from idw import fill_missing_data


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
    data = fill_missing_data(data, -2.0e+9)

    return x, y, data
