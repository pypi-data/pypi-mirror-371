from scipy.linalg import null_space
import numpy as np

def get_eigenvectors(A, eigenvalue):
    return null_space(A - eigenvalue * np.eye(len(A)))
