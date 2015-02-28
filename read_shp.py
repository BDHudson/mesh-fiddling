
import numpy as np
from shapefile import *

# ---------------------------
def read_shapefile(filename):
    sf = Reader(filename)

    X = []
    Y = []

    for shape in sf.shapes():
        x = []
        y = []

        num_pts = len(shape.points)

        if num_pts > 0:
            for i in range(num_pts):
                x.append(shape.points[i][0])
                y.append(shape.points[i][1])

            X.append(x)
            Y.append(y)

    return X, Y


# -----------------------------
def read_shapefiles(filenames):
    X = []
    Y = []

    for filename in filenames:
        x, y = read_shapefile(filename)
        X.extend(x)
        Y.extend(y)

    return X, Y
