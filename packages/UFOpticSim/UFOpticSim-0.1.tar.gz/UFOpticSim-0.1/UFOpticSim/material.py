from .calc import *

class Material:
    def __init__(self, media: str, thickness_mm: float) -> None:
        self.media = media
        self.thickness_mm = thickness_mm
        try:
            self.B = B_Materials[self.media]
            self.C = C_Materials[self.media]
        except:
            raise ValueError(f"Material name: {self.media} not defined!")
        
    def get_n(self, wavelength: float) -> float:
        return sellmeier_n(wavelength, self.B, self.C)
    
    def compute_gvd(self, central_wavelength_nm: float) -> float:
        w0 = 2*c_pi*c_c / (central_wavelength_nm * 1e-9)
        lambda0_um = central_wavelength_nm * 1e-3

        # Use central difference method
        d_lambda = 0.001  # small step in µm
        lambdas = lambda0_um + np.array([-d_lambda, 0, d_lambda])
        ns = sellmeier_n(lambdas, self.B, self.C)
        omegas = 2 * c_pi * c_c / (lambdas * 1e-6)  # rad/s

        # Interpolate n(omega) and obtain central values
        dn_domega = np.gradient(ns, omegas)
        d2n_domega2 = np.gradient(dn_domega, omegas)
        dn_dw = dn_domega[1]
        d2n_dw2 = d2n_domega2[1]

        # Calculate GDD
        L = self.thickness_mm / 1000  # m

        gvd = (2 * dn_dw + w0 * d2n_dw2) / c_c

        return gvd