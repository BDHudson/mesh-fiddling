
from read_shp import *
from mesh_fiddling import *
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

    if output_filename[-5:] == ".poly":
        write_to_triangle(output_filename, X, Y)
    else:
        write_to_geo(output_filename, X, Y)
