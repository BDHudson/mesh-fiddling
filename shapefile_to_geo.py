import numpy as np
import shapefile
import itertools
from matplotlib.path import Path
import sys


class GeometryError(Exception):
    pass


def get_shape(filename):
    sf = shapefile.Reader(filename)
    shape = sf.shapes()[0]
    return shape


def extract_parts(shape):
    parts = shape.parts
    parts.append(len(shape.points))

    points = np.asarray(shape.points)
    Xs = []
    for k in range(len(parts) - 1):
        p1, p2 = parts[k], parts[k + 1]
        # Check that the -1 is right, QGIS inserts a duplicate 
        # point at the end of the polygon
        Xs.append(points[p1: p2 - 1, :])

    return Xs


def find_exterior_part(Xs):
    """
    Find which part of the Shape is contains all the others.
    Raises a GeometryError in the event that the shape is badly-formed,
    i.e. it consists of more than one connected component, there are
    intersecting parts, etc.

    This is probably going to be the first shape in almost every
    circumstance, but I don't feel like finding out the hard way that
    QGIS decided to muck with the order that it writes shapefiles in.
    """
    outermost = np.ones(len(Xs), dtype = bool)
    Paths = map(lambda X: Path(X[:-1, :]), Xs)
    for k, l in itertools.combinations(range(len(Paths)), 2):
        P = Paths[k]
        Q = Paths[l]

        outermost[k] &= P.contains_path(Q)
        outermost[l] &= Q.contains_path(P)

    num_exterior_parts = sum(outermost)
    if num_exterior_parts > 1:
        raise GeometryError("Non-unique exterior component.")
    if num_exterior_parts == 0:
        raise GeometryError("No exterior component found.")

    return np.argmax(outermost)


def shapefile_to_geo(shp_filename, geo_filename):
    Xs = extract_parts(get_shape(shp_filename))
    N = find_exterior_part(Xs)

    num_parts = len(Xs)
    offset = np.zeros(num_parts + 1, dtype = np.int32)
    offset[0] = 1
    for p in range(num_parts):
        offset[p+1] = offset[p] + len(Xs[p])

    geo = open(geo_filename, "w")
    cl = 1.0e+3
    geo.write("cl = {0};\n\n".format(cl))
    geo.write("// Mesh points\n")
    for p in range(num_parts):
        X = Xs[p]
        for k in range(len(X)):
            geo.write("Point({0}) = {{{1}, {2}, 0, cl}};\n"
                      .format(offset[p] + k, X[k, 0], X[k, 1]))
    geo.write("\n")

    geo.write("// Edges\n")
    for p in range(num_parts):
        n = len(Xs[p])
        for k in range(n):
            i = offset[p] + k
            j = offset[p] + (k + 1) % n
            geo.write("Line({0}) = {{{1}, {2}}};\n"
                      .format(offset[p] + k, i, j))
    geo.write("\n")

    geo.write("// Line loops\n")
    for p in range(num_parts):
        geo.write("Line Loop({0}) = {{{1}"
                  .format(offset[-1] + p, offset[p]))
        n = len(Xs[p])
        for k in range(1, n):
            i = offset[p] + k
            geo.write(", {0}".format(offset[p] + k))
        geo.write("};\n")
    geo.write("\n")

    geo.write("Plane Surface({0}) = {{{1}"
              .format(offset[-1] + num_parts, offset[-1]))
    for p in range(1, num_parts):
        geo.write(", {0}".format(offset[-1] + p))
    geo.write("};\n\n")

    geo.write("Recombine Surface{{{0}}};\n"
              .format(offset[-1] + num_parts))
    geo.write("\n")

    geo.write("Mesh.Algorithm = 8;\n\n")

    geo.close()



if __name__ == "__main__":
    shp_filename = sys.argv[1]
    geo_filename = sys.argv[2]
    shapefile_to_geo(shp_filename, geo_filename)

