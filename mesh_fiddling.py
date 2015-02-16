from numpy import ones, zeros, sqrt
from matplotlib.path import *
from itertools import combinations


def next_segment(X, Y, i, tol = 1000.0):
    """
    Find all segments adjacent to segment `i` in the list-of-lines `X, Y`
    """
    num_segments = len(X)

    Xi = X[i]
    Yi = Y[i]

    for j in range(num_segments):
        if j != i:
            Xj = X[j]
            Yj = Y[j]

            dist = sqrt((Xi[-1] - Xj[0])**2 + (Yi[-1] - Yj[0])**2)
            if dist < tol:
                return j

            dist = sqrt((Xi[-1] - Xj[-1])**2 + (Yi[-1] - Yj[-1])**2)
            if dist < tol:
                return -j

    return i


# -----------------------------------------
def segment_successors(X, Y, tol = 1000.0):
    """
    Parameters:
    ==========
    X, Y: list of lists of the coordinates of each line

    Returns:
    =======
    W, Z:       modified coordinates; some segments may be reversed
    successors: successors[i] = the next segment after `i`
    """

    num_segments = len(X)

    # Make copies of the input arrays; we'll be modifying them
    W = X[:]
    Z = Y[:]

    segments = set(range(num_segments))
    successors = range(num_segments)

    while segments:
        i0 = segments.pop()

        i = i0
        j = next_segment(W, Z, i, tol)
        while j != i0:
            if j < 0:
                j = -j
                W[j].reverse()
                Z[j].reverse()

            segments.remove(j)
            successors[i] = j

            i = j
            j = next_segment(W, Z, i, tol)

        successors[i] = i0

    return W, Z, successors


# -----------------------------------
def lines_to_paths(X, Y, successors):
    num_segments = len(X)
    segments = set(range(num_segments))
    ps = []

    while segments:
        i0 = segments.pop()
        i = i0

        arr = zip(X[i], Y[i])

        j = next_segment(X, Y, i)
        while j != i0:
            segments.remove(j)
            arr.extend(zip(X[j], Y[j]))

            i = j
            j = next_segment(X, Y, i)

        p = Path(arr, closed = True)
        ps.append(p)

    return ps


# -----------------------
def point_inside_path(p):
    """
    Return a somewhat arbitrary point inside the path p.
    Triangle needs to have a point contained in any holes in the mesh.
    """

    x = 0.0
    y = 0.0

    i = 0
    j = len(p)/2
    # This is sloppy, don't care
    while not p.contains_point((x, y)):
        j += 1
        x = 0.5 * (p.vertices[i, 0] + p.vertices[j, 0])
        y = 0.5 * (p.vertices[i, 1] + p.vertices[j, 1])

    return x, y


# -----------------------------------
def identify_holes(X, Y, successors):
    """
    Find which segments of the PSLG are the outlines of holes in the mesh
    """
    xh = []
    yh = []

    ps = lines_to_paths(X, Y, successors)
    for p, q in combinations(ps, 2):
        if p.contains_path(q):
            w, z = point_inside_path(q)
            xh.append(w)
            yh.append(z)

    return xh, yh


# --------------------------
def write_to_triangle(filename, X, Y, tol = 1000.0):
    """
    Write out a .poly file
    """
    W, Z, successors = segment_successors(X, Y)

    num_segments = len(W)
    num_points = sum([len(w) for w in W])

    poly_file = open(filename, "w")
    poly_file.write("{0} 2 0 1\n".format(num_points))

    # Write out the PSLG points
    counter = 1
    for k in range(num_segments):
        w, z = W[k], Z[k]

        for i in range(len(w)):
            poly_file.write("{0} {1} {2} {3}\n"
                            .format(counter + i, w[i], z[i], k))

        counter += len(w)


    # Write out the PSLG edges
    poly_file.write("{0} 1\n".format(num_points))

    offsets = zeros(num_segments + 1, dtype = int)
    offsets[0] = 1
    for k in range(num_segments):
        offsets[k + 1] = offsets[k] + len(W[k])

    counter = 1
    for k in range(num_segments):
        w, z = W[k], Z[k]

        # Write out all the edges within this segment
        for i in range(len(w) - 1):
            poly_file.write("{0} {1} {2} {3}\n"
                            .format(counter + i,
                                    offsets[k] + i,
                                    offsets[k] + i + 1,
                                    k + 1))

        # Write out the edge connecting this segment to the next.
        # Note that if this segment is its own successor, this just
        # connects the tail back to the head.
        l = successors[k]
        poly_file.write("{0} {1} {2} {3}\n"
                        .format(counter + len(w) - 1,
                                offsets[k] + len(w) - 1,
                                offsets[l],
                                k + 1))

        counter += len(w)

    # Write out the PSLG holes
    xh, yh = identify_holes(W, Z, successors)
    num_holes = len(xh)
    poly_file.write("{0}\n".format(num_holes))
    for i in range(num_holes):
        poly_file.write("{0} {1} {2}\n".format(i + 1, xh[i], yh[i]))

    poly_file.close()


# ------------------------------------
def write_to_geo(filename, X, Y, tol = 1000.0):
    """
    Write out the PSLG to the gmsh .geo format
    """
    W, Z, successors = segment_successors(X, Y)

    num_segments = len(W)
    num_points = sum([len(w) for w in W])

    geo_file = open(filename, "w")

    # Write out the PSLG points
    counter = 1
    for k in range(num_segments):
        w, z = W[k], Z[k]

        for i in range(len(w)):
            geo_file.write("Point({0}) = {{{1}, {2}}};\n"
                           .format(counter + i, w[i], z[i]))

        counter += len(w)


    # Write out the PSLG edges
    offsets = zeros(num_segments + 1, dtype = int)
    offsets[0] = 1
    for k in range(num_segments):
        offsets[k + 1] = offsets[k] + len(W[k])

    counter = 1
    for k in range(num_segments):
        w, z = W[k], Z[k]

        for i in range(len(w) - 1):
            geo_file.write("Line({0}) = {{{1}, {2}}};\n"
                           .format(counter + i,
                                   offsets[k] + i,
                                   offsets[k] + i + 1))

        l = successors[k]
        poly_file.write("Line({0}) = {{{1}, {2}}};\n"
                        .format(counter + len(w) - 1,
                                offsets[k] + len(w) - 1,
                                offsets[l]))

        counter += len(w)
