class Results:
    def __init__(self, sim):
        self.sim = sim
        # Set the defaults
        self.GDD_fs2 = 0
        self.central_wavelength_nm = self.sim.pulse.beam.central_wavelength_nm
        self.bandwidth_nm = self.sim.pulse.beam.bandwidth_nm
        self.beam_size_mm = self.sim.pulse.beam.beam_waist_mm

    def set_basic_beam_properties(self, E_t, t, E_w, w):
        self.E_t = E_t
        self.t = t
        self.E_w = E_w
        self.w = w

    def set_central_wavelength(self, central_wavelength_nm: float, bandwidth_nm: float):
        self.central_wavelength_nm = central_wavelength_nm
        self.bandwidth_nm = bandwidth_nm

    def set_beam_size(self, new_beam_size_nm: float):
        self.beam_size_mm = new_beam_size_nm

    def set_GDD(self, GDD_fs2: float):
        self.GDD_fs2 = GDD_fs2

    def add_GDD(self, GDD_fs2: float):
        self.GDD_fs2 += GDD_fs2

    def set_duration(self, duration_fs: float):
        self.duration_fs = duration_fs

    def plot_temporal_profile(self):
        pass

    def plot_spectrum(self):
        pass

    def plot_phase_vs_freq(self):
        pass

    def plot_beam_size_evolution(self):
        pass

    def print(self):
        print("\nAfter Propagation")
        print("-----------------")
        print("\n1. Temporal Properties")
        print(f"\tPulse Duration (FWHM): {self.duration_fs} fs")
        print(f"\tChirp GDD = {self.GDD_fs2} fs^2")
        print("\n2. Spectral Properties")
        print(f"\tCentral Wavelength: {self.central_wavelength_nm} nm")
        print(f"\tBandwidth: {self.bandwidth_nm} nm")
        print("\n3. Spatial Properties")
        print(f"\tBeam Waist: {self.beam_size_mm} mm")
        print()
