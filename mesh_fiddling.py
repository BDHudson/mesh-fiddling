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


# --------------------------
def remove_coincident_endpoints(X, Y, seg_tol = 1000.0, node_tol = 200.0):
    num_segments = len(X)
    segments = set(range(num_segments))

    while segments:
        i = segments.pop()
        j = next_segment(X, Y, i, seg_tol)
        while j in segments:
            segments.remove(j)

            dist = sqrt((X[i][-1] - X[j][0])**2 + (Y[i][-1] - Y[j][0])**2)
            if dist < node_tol:
                X[i].pop()
                Y[i].pop()
                
            i = j
            j = next_segment(X, Y, i, seg_tol)


# --------------------------
def write_to_triangle(filename, X, Y, tol = 1000.0):
    """
    Write out a .poly file
    """
    W, Z, s = segment_successors(X, Y)
    remove_coincident_endpoints(W, Z, seg_tol = tol)
    num_segments = len(W)

    poly_file = open(filename + ".poly", "w")
    poly_file.write("{0} 2 0 1\n".format(sum([len(w) for w in W])))

    # Write out the PSLG points
    num_points = 1
    for k in range(num_segments):
        w, z = W[k], Z[k]

        for i in range(len(w)):
            poly_file.write("{0} {1} {2} {3}\n"
                            .format(num_points + i, w[i], z[i], k))

        num_points += len(w)

    poly_file.close()

