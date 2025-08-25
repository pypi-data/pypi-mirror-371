"""
inverse_laplace - Numerical Inverse Laplace Transform using Talbot's Method.

This module provides efficient computation of the inverse Laplace transform using Talbot’s method,
suitable for engineering, physics, and mathematical applications.

Dependencies:
    - sympy
    - mpmath
"""

import sympy as sp
import mpmath
from functools import lru_cache
from multiprocessing import Pool, cpu_count

t, s = sp.symbols('t s')

@lru_cache(maxsize=None)
def get_lambdified_func(F):
    return sp.lambdify(s, F, 'mpmath')

def inverse_laplace(F, t_val):
    if t_val <= 0:
        return 0.0
    F_func = get_lambdified_func(F)
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

# Public API
__all__ = ['inverse_laplace']
