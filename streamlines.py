import numpy as np
from shapefile import *
from geodat import read_geodat

# -------------------------------
def interpolate(x, y, x0, y0, q):
    """
    Interpolate the value of the field `q` defined on the grid `x`, `y`
    to the point `x0`, `y0`
    """
    dx = x[1]-x[0]
    dy = y[1]-y[0]

    i = int( (y0-y[0])/dy )
    j = int( (x0-x[0])/dx )

    alpha_x = (x0 - x[j]) / dx
    alpha_y = (y0 - y[i]) / dy

    p = (q[i,j]
            + alpha_x * (q[i, j + 1] - q[i, j])
            + alpha_y * (q[i + 1, j] - q[i, j])
            + alpha_x * alpha_y * (q[i + 1, j + 1] + q[i, j]
                                     - q[i + 1, j] - q[i, j + 1]))

    return p


# ---------------------------------------------
def streamline(x, y, vx, vy, x0, y0, sign = 1):
    """
    Given the x/y velocity fields `vx`, `vy`, defined at the grid points
    `x`, `y`, generate a streamline originating at the point `x0`, `y0`.
    The streamline will go backwards if the optional argument `sign` = -1.

    The algorithm we use is an adaptive forward Euler method. It's not very
    good. Willie hears ye; Willie don't care.

    Parameters:
    ==========
    x, y: coordinates at which the fields are defined
    vx, vy: velocities in the x, y directions
    x0, y0: starting coordinate of the streamline
    sign: optional; =1 if the streamline is forward, -1 if backward

    Returns:
    =======
    X, Y: coordinates of the resultant streamline
    """
    nx = len(x)
    ny = len(y)

    u = interpolate(x, y, x0, y0, vx)
    v = interpolate(x, y, x0, y0, vy)

    speed = np.sqrt(u**2 + v**2)

    X = [ x0 ]
    Y = [ y0 ]

    k = 0

    while (speed > 5.0 and k < 10000):
        k += 1
        dt = sign * 50.0 / speed

        x0 = x0 + dt * u
        y0 = y0 + dt * v

        X.append(x0)
        Y.append(y0)

        u = interpolate(x, y, x0, y0, vx)
        v = interpolate(x, y, x0, y0, vy)
        speed = np.sqrt(u**2 + v**2)

    return X, Y


# --------------------------------
def coarsen_streamline(X, Y, res):
    """
    Parameters:
    ==========
    x, y: coordinates of a path
    res:  resolution of the coarsening

    Returns:
    =======
    X, Y: coordinates of the coarsened path
    """

    nn = len(X)

    Xc = []
    Yc = []

    Xc.append(X[0])
    Yc.append(Y[0])

    for i in range(1, nn):
        # Should probably do some correction for the curvature
        dist = np.sqrt((X[i] - Xc[-1])**2 + (Y[i] - Yc[-1])**2)
        if dist > res:
            Xc.append(X[i])
            Yc.append(Y[i])

    return Xc, Yc


# ---------------------------------------------------------------
def streamlines_from_shapefile(x, y, vx, vy, filename, sign = 1):
    """
    Given an ESRI shapefile, read in all the points it contains and
    generate streamlines from them.

    Parameters:
    ==========
    x, y, vx, vy: same as in last function
    filename: name of .shp file from which we get start points

    Returns:
    =======
    lines: array of streamlines
    """

    sf = Reader(filename)
    shape = sf.shapes()[0]
    num_pts = len(shape.points)

    X0 = np.zeros(num_pts, dtype = np.float64)
    Y0 = np.zeros(num_pts, dtype = np.float64)

    for i in range(num_pts):
        X0[i] = shape.points[i][0]
        Y0[i] = shape.points[i][1]

    lines = []

    for i in range(num_pts):
        X, Y = streamline(x, y, vx, vy, X0[i], Y0[i], sign)

        line = []
        for k in range(len(X)):
            line.append([X[k], Y[k]])
        lines.append(line)

    return lines


# -------------------------------------
def write_streamlines(lines, filename):
    """
    Given an array of streamlines, write them out to a shapefile.

    Parameters:
    ==========
    lines: array of arrays of tuples, coordinates along each streamline
    filename: name for output file
    """

    strm = Writer()
    strm.autoBalance = 1
    strm.field('FIELD', 'C', '1')

    for line in lines:
        strm.line(parts = [line])
        strm.record('')

    strm.save(filename)


# -------------------------------------
def make_streamlines(velocity_filename,
                     initial_shapefile,
                     streamlines_shapefile,
                     inflow = 1):
    """
    Parameters:
    ==========
    velocity_filename:     stem of the geodat filenames for the ice
                           velocities
    initial_shapefile:     shapefile containing the points from which
                           to create the streamlines
    streamlines_shapefile: shapefile to write streamlines to
    inflow:                optional argument; specify whether the start
                           points are at the glacier inflow or outflow
    """

    x, y, vx = read_geodat(velocity_filename + ".vx")
    x, y, vy = read_geodat(velocity_filename + ".vy")

    ny, nx = np.shape(vx)
    for i in range(ny):
        for j in range(nx):
            if vx[i, j] == -2.0e+9:
                vx[i, j] = 0.0
                vy[i, j] = 0.0

    lines = streamlines_from_shapefile(x, y, vx, vy,
                                       initial_shapefile, inflow)

    write_streamlines(lines, streamlines_shapefile)
