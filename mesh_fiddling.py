from numpy import ones, zeros, sqrt


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

    return W, Z, successors


# ----------------------
def lines_to_pslg(X, Y):
    """
    Given a list of lines of input points, create a planar straight-line
    graph (PSLG) such as would be used for input to Triangle or gmsh.

    Parameters:
    ==========
    X, Y: list of lists of the coordinates of each line

    Returns:
    =======
    x, y:   numpy arrays of coordinates of PSLG points
    edges:  list of edges of the PSLG
    bndry:  boundary marker for each edge of the PSLG
    xh, yh: list of points inside the holes of the PSLG
    """
