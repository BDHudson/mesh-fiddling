import numpy as np

# --------------------------------
def adjacency(X, Y, tol = 1000.0):
    """
    Parameters:
    ==========
    X, Y: list of lists of the coordinates of each line

    Returns:
    =======
    adj: Integer matrix describing the connectivity among the lines;
         adj[i, j] != 0 if lines i, j are adjacent; = +1 if the orientation
         of line `i` is preserved, -1 if the orientation is to be reversed.
    """

    nc = len(X)
    adj = np.zeros((nc, nc), dtype = np.int32)

    for i in range(nc):
        Xi = X[i]
        Yi = Y[i]

        for j in range(nc):
            if i != j:

                Xj = X[j]
                Yj = Y[j]

                dist01 = np.sqrt((Xi[0] - Xj[-1])**2 + (Yi[0] - Yj[-1])**2)
                dist00 = np.sqrt((Xi[0] - Xj[0])**2 + (Yi[0] - Yj[0])**2)
                dist10 = np.sqrt((Xi[-1] - Xj[0])**2 + (Yi[-1] - Yj[0])**2)
                dist11 = np.sqrt((Xi[-1] - Xj[-1])**2 + (Yi[-1] - Yj[-1])**2)

                if dist01 < tol or dist10 < tol:
                    adj[i, j] = 1
                    adj[j, i] = 1

                if dist00 < tol or dist11 < tol:
                    adj[i, j] = -1
                    adj[j, i] = -1

    return adj


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

    num_segments = len(X)

    adj = adjacency(X, Y)

    successor = -np.ones(num_segments, dtype = np.int32)
    undiscovered = set(range(num_segments))

    while undiscovered:
        # Pick a segment that we haven't analyzed yet
        i0 = undiscovered.pop()
        i = i0

        # If that segment is connected to any others, depth-first search
        # through the adjacency graph and assign a successor to each
        # segment.
        stack = list(adj[i,:].nonzero()[0])
        for j in stack:
            undiscovered.remove(j)

        while stack:
            j = stack.pop()
            successor[i] = j

            i = j
            for j in adj[i,:].nonzero()[0]:
                if j in undiscovered:
                    stack.append(j)
                    undiscovered.remove(j)

        # Close the loop by finding the last segment in the depth-first
        # search and assigning the initial segment as its successor.
        i = successor[i0]
        if i != -1:
            while successor[i] != -1:
                i = successor[i]
            successor[i] = i0
            

    return successor
