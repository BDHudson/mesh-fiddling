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
            Xj = X[j]
            Yj = Y[j]

            dist01 = np.sqrt((Xi[0] - Xj[-1])**2 + (Yi[0] - Yj[-1])**2)
            dist00 = np.sqrt((Xi[0] - Xj[0])**2 + (Yi[0] - Yj[0])**2)
            dist10 = np.sqrt((Xi[-1] - Xj[0])**2 + (Yi[-1] - Yj[0])**2)
            dist11 = np.sqrt((Xi[-1] - Xj[-1])**2 + (Yi[-1] - Yj[-1])**2)

            if (dist01 < tol or dist00 < tol
                or dist10 < tol or dist11 < tol):
                adj[i, j] = 1
                adj[j, i] = 1

    return adj


# ----------------------
def lines_to_pslg(X, Y):
    """
    Parameters:
    ==========
    X, Y: list of lists of the coordinates of each line

    Returns:
    =======
    x, y: numpy arrays of coordinates of PSLG points
    edges: 
    bndry:
    xh, yh:
    """

    adj = adjacency(X, Y)


