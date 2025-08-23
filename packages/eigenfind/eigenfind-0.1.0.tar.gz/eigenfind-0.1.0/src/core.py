import src.numeric as numeric, src.symbolic as symbolic

def get_eigenvectors_by_value(A, eigenvalue, mode='numeric'):
    if mode == 'numeric':
        return numeric.get_eigenvectors(A, eigenvalue)
    elif mode == 'symbolic':
        return symbolic.get_eigenvectors(A, eigenvalue)
