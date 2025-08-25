import math
from typing import Callable
import numpy as np

c_c = 299792458
c_pi = 3.14159265358979

# B and C constants for different materials, used to calculate sellmeier_n
B_Materials = {
    'air': [
        0.05792105,
        0.00167917,
        0
    ],
    'BK7': [
        1.03961212,
        0.231792344,
        1.01046945
    ]
}

C_Materials = {
    'air': [
        238.0185, 
        57.362,
        0
    ],
    'BK7': [
        6.00069867e-3,
        2.00179144e-2,
        1.03560653e+2
    ]
}

def c_to_rad(deg):
    return (deg % 360) * 2 * c_pi / 360

def c_to_deg(rad):
    return (rad * 360 / (2 * c_pi)) % 360

def derivative(f: Callable, x0: float, dx: float = 1e-5, n: int = 1) -> float:
    if n == 1:
        return (f(x0 + dx) - f(x0 - dx)) / (2 * dx)
    elif n == 2:
        return (f(x0 + dx) - 2 * f(x0) + f(x0 - dx)) / dx**2
    elif n == 3:
        return (f(x0 - 2*dx) - 2*f(x0 - dx) + 2*f(x0 + dx) - f(x0 + 2*dx)) / (2*dx**3)
    else:
        raise ValueError("Only the first three derivatives are supported")

def sellmeier_n(wavelength: float, B: list, C: list) -> float:
    s = 1
    for i in range(3):
        s += B[i] * (wavelength**2) / (wavelength**2 - C[i])
    return np.sqrt(s)

