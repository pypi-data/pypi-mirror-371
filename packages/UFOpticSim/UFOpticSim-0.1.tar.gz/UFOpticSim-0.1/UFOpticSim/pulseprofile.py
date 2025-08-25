from .calc import *

class PulseProfile:
    def __init__(self, duration_fs: float, bandwidth_nm, central_wavelength_nm: float, is_temporally_limited: bool,  beam_waist_mm: float, m2: float):
        self.duration_fs = duration_fs
        self.central_wavelength_nm = central_wavelength_nm
        self.bandwidth_nm = bandwidth_nm
        if is_temporally_limited:
            self.temporal_width = 0.441 / (self.bandwidth_nm * 1e-9)
        self.beam_waist_mm = beam_waist_mm
        self.central_wavelength_nm = central_wavelength_nm
        self.m2 = m2
        self.rayleigh = c_pi * (self.beam_waist_mm * 1e-3) ** 2 / (self.central_wavelength_nm * 1e-9)
        self.beam_radius = lambda z: (self.beam_waist_mm * 1e-3) * math.sqrt(1 + (z / self.rayleigh) ** 2)
        self.curvature = lambda z: z * (1 + (self.rayleigh / z) ** 2)
        self.gouy = lambda z: math.atan2(z, self.rayleigh)