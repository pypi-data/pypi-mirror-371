# Symbolic implementation using SymPy.

# Solves exact nullspace for symbolic matrices or rational numbers.
# symbolic.py
from sympy import Matrix

def get_eigenvectors(matrix, eigenvalue):
    """
    Returns the eigenvectors for a given eigenvalue using symbolic math (SymPy).
    
    Parameters:
    - matrix: a list of lists or sympy.Matrix representing a square matrix
    - eigenvalue: a number or symbolic expression
    
    Returns:
    - list of sympy Matrix columns representing eigenvectors
    """
    if not isinstance(matrix, Matrix):
        matrix = Matrix(matrix)
    
    n = matrix.shape[0]
    identity = Matrix.eye(n)
    
    # Form (A - λI)
    eig_matrix = matrix - eigenvalue * identity
    
    # Return the nullspace (eigenspace) as a list of column vectors
    return eig_matrix.nullspace()

    from sympy import symbols

# λ = symbols('λ') TBD
# get_eigenvectors(A, λ)
