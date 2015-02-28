
import numpy as np
from itertools import izip

def find_missing_point(q, missing):
    """
    Find a point on the edge of the dataset q which is missing data
    """
    ny, nx = np.shape(q)
    lower_boundary = np.where(q[0,:] == missing)[0]
    if len(lower_boundary) > 0:
        return 0, lower_boundary[0]

    upper_boundary = np.where(q[ny - 1, :] == missing)[0]
    if len(upper_boundary) > 0:
        return ny - 1, upper_boundary[0]

    left_boundary = np.where(q[:, 0] == missing)[0]
    if len(left_boundary) > 0:
        return left_boundary[0], 0

    right_boundary = np.where(q[:, nx - 1] == missing)[0]
    if len(right_boundary) > 0:
        return right_boundary[0], nx - 1

    return []


def exterior_mask(q, missing):
    """
    Find the connected components of a gridded dataset, divided along
    boundaries of having/missing data.
    """
    ny, nx = np.shape(q)
    mask = np.zeros((ny, nx), dtype = bool)

    i, j = find_missing_point(q, missing)
    mask[i, j] = True
    stack = [ (i, j) ]

    while stack:
        i, j = stack.pop()

        for (k, l) in [ ( (i+1)%ny, j ),
                        ( (i-1)%ny, j ),
                        ( i, (j+1)%nx ),
                        ( i, (j-1)%nx ) ]:
            if q[k, l] == missing and not mask[k, l]:
                mask[k, l] = True
                stack.append( (k, l) )

    return mask


def fill_missing_data(q, missing, d = 12):
    """
    Take a gridded data set and fill in any interior points that are missing
    data using inverse-distance weighting.
    """
    ny, nx = np.shape(q)
    exterior = exterior_mask(q, missing)
    p = np.copy(q)

    I, J = np.where(q == missing)
    for i, j in izip(I, J):
        if not exterior[i, j]:
            weights = 0.0
            p[i, j] = 0.0
            for di in range(-d, d+1):
                for dj in range(-d, d+1):
                    k = i + di
                    l = j + dj

                    if q[k, l] != missing and not (i == k and j == l):
                        weight = 1.0 / np.sqrt(di**2 + dj**2)**3
                        p[i, j] += weight * q[k, l]
                        weights += weight

            if weights != 0.0:
                p[i, j] /= weights
            else:
                print("Unable to interpolate at {0}, {1}\n".format(i, j))

    return p
