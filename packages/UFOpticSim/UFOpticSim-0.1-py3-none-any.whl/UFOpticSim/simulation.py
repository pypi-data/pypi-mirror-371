from .laser import Laser
from .screen import Screen
from .lens import Lens
from .mirror import Mirror
from .prism import Prism
from .grating import Grating
from .results import Results
from .material import Material
from .calc import *

import threading

class Simulation:
    def __init__(self, media: str, interval_cm: float = 1):
        self.media = media
        self.interval_cm = interval_cm
        self.space = []
        self.elements = []

    def add_laser(self, laser: Laser):
        self.pulse = laser
        self.lambda0 = self.pulse.beam.central_wavelength_nm * 1e-9
        self.w0 = 2 * c_pi * c_c / self.lambda0
        self.laser_pos = self.pulse.pos()

    def add_element(self, element):
        assert type(element) == Lens or type(element) == Grating or type(element) == Mirror or type(element) == Prism
        self.elements.append(element)

    def add_screen(self, screen: Screen):
        self.screen = screen

    def find_element_with_pos(self, pos_cm2: tuple):
        if self.pulse.pos() == pos_cm2:
            return self.pulse
        for element in self.elements:
            if element.pos() == pos_cm2:
                return element
        if self.screen.pos() == pos_cm2:
            return self.screen
        return None
        
    def move(self):
        self.laser_pos[0] += self.pulse.dirx * self.interval_cm
        self.laser_pos[1] += self.pulse.diry * self.interval_cm

    def output(self):
        self.print()
        results = self.get_results()
        results.print()

    def get_results(self) -> Results:
        result = Results(self)

        gdd = 0

        element_history = []
        i = 0
        while self.laser_pos != self.screen.pos():
            self.move()
            element = self.find_element_with_pos(self.laser_pos)
            if element != None:
                element_history.append(element)
                # Find GDD of the space between the elements
                if i == 0:
                    distance_to_last_element_cm = math.sqrt((element.x - self.pulse.x)**2 + (element.y - self.pulse.y)**2)
                elif i != len(self.elements) - 1:
                    distance_to_last_element_cm = math.sqrt((element.x - element_history[-2].x)**2 + (element.y - element_history[-2].y)**2)
                else:
                    distance_to_last_element_cm = math.sqrt((element.x - self.screen.x)**2 + (element.y - self.screen.y)**2)
                
                gdd = distance_to_last_element_cm * 1e-2 * Material(media=self.media, thickness_mm=distance_to_last_element_cm * 10).compute_gvd(central_wavelength_nm=self.lambda0 * 1e+9)
                gdd *= 1e+30
                result.add_GDD(gdd)

                if type(element) == Grating:
                    pass
                
                if type(element) == Lens or type(element) == Prism or type(element) == Mirror:
                    # GDD Calculation from material GVD
                    L = element.material.thickness_mm * 1e-3
                    gdd = L * element.material.compute_gvd(central_wavelength_nm=self.lambda0 * 1e+9)
                    gdd *= 1e+30 # fs²
                    result.add_GDD(gdd)

                if type(element) == Mirror:
                    phi = 2 * c_pi - math.atan2(self.pulse.diry, self.pulse.dirx)
                    theta = c_to_rad(180 - element.angle)
                    phi_prime = 2 * theta + 3 * phi - c_pi
                    self.pulse.dirx = round(math.cos(phi_prime))
                    self.pulse.diry = round(math.sin(phi_prime))

                if type(element) == Lens:
                    # Beam Waist calculations
                    spot_size_mm = 4 * element.focal_length_mm * (self.lambda0 * 1e+3) * self.pulse.beam.m2 / (c_pi * self.pulse.beam.beam_waist_mm)
                    distance_to_screen_mm = 10 * math.sqrt((element.x - self.screen.x)**2 + (element.y - self.screen.y)**2)
                    depth_of_field_mm = 2 * c_pi * (spot_size_mm / 2) ** 2 / (self.lambda0 * 1e+3 * self.pulse.beam.m2)
                    new_beam_diameter_mm = spot_size_mm * math.sqrt(1 + ((distance_to_screen_mm - element.focal_length_mm)**2) / (depth_of_field_mm / 2)**2)
                    result.set_beam_size(new_beam_diameter_mm)

                i += 1

        # Beam Duration changes due to chirping
        result.set_duration(self.pulse.beam.duration_fs * math.sqrt(1 + (4*math.log(2) * gdd / self.pulse.beam.duration_fs**2)**2))

        return result


    def start_visualisation(self):
        import pygame

        pygame.init()
        pygame.display.set_caption("Optical Simulation Visualising Tool")
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont("Times New Roman", 10)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))

            self.pulse.draw(screen, font)
            self.screen.draw(screen, font)
            
            for element in self.elements:
                element.draw(screen, font)

            pygame.display.update()

        pygame.quit()

    def run(self, output: bool = True, visualisation: bool = True):
        if output and visualisation:
            t1 = threading.Thread(target=self.start_visualisation, args=())
            t2 = threading.Thread(target=self.output, args=())
            t1.start()
            t2.start()

    def print(self):
        print("\nInput Pulse")
        print("-----------")
        print("\n1. Temporal Properties")
        print(f"\tPulse Duration (FWHM): {self.pulse.beam.duration_fs} fs")
        print("\n2. Spectral Properties")
        print(f"\tCentral Wavelength: {self.pulse.beam.central_wavelength_nm} nm")
        print(f"\tBandwidth: {self.pulse.beam.bandwidth_nm} nm")
        print("\n3. Spatial Properties")
        print()
