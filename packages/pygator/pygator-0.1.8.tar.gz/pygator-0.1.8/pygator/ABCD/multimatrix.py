# my_package/__init__.py
# from pygator.module import *
# from ._version import __version__

# pygator/__init__.py
import numpy as np

def multiply_abcd(*matrices, reverse=True, q_in=None):
    """
    Multiply an arbitrary number of ABCD matrices and optionally 
    propagate a Gaussian beam q-parameter.

    Parameters
    ----------
    *matrices : array-like
        Any number of 2x2 numpy arrays representing ABCD matrices.
        Example: multiply_abcd(M1, M2, M3)

    reverse : bool, optional (default=True)
        If True, multiply in reverse order (optical convention: 
        beam hits last matrix first).
        If False, multiply in given order.

    q_in : complex or None, optional
        Input Gaussian beam q-parameter. If provided, the output q 
        after propagation is also returned.

    Returns
    -------
    result : ndarray
        2x2 numpy array representing the combined ABCD matrix.

    q_out : complex (optional)
        Output q-parameter if q_in is given.
    """

    # Ensure all are numpy arrays
    mats = [np.array(M, dtype=float) for M in matrices]

    # Reverse order if needed
    if reverse:
        mats = mats[::-1]

    # Multiply sequentially
    result = np.eye(2)
    for M in mats:
        result = result @ M

    if q_in is not None:
        A, B, C, D = result.ravel()
        q_out = (A * q_in + B) / (C * q_in + D)
        return result, q_out

    return result
