
from read_shp import read_shapefiles
from mesh_fiddling import write_to_triangle, write_to_geo
from streamlines import coarsen_streamline
import glob
import sys


if __name__ == "__main__":
    output_filename = sys.argv[1]

    input_filenames = []
    for pattern in sys.argv[2:]:
        input_filenames.extend(glob.glob(pattern))

    # Get rid of any input that's not a shapefile
    input_filenames = [s for s in input_filenames if s[-4:] == ".shp"]

    X, Y = read_shapefiles(input_filenames)

    for k in range(len(X)):
        X[k], Y[k] = coarsen_streamline(X[k], Y[k], 500.0)

    if output_filename[-5:] == ".poly":
        write_to_triangle(output_filename, X, Y)
    else:
        write_to_geo(output_filename, X, Y)
