import pygame
import math

from .material import Material
from .calc import *

class Mirror:
    def __init__(self, material: Material, angle_to_horizontal: float, pos_cm2: tuple, mirror_name: str) -> None:
        self.material = material
        assert 0 <= angle_to_horizontal < 360
        self.angle = angle_to_horizontal
        self.x = pos_cm2[0]
        self.y = pos_cm2[1]
        self.mirror_name = mirror_name

    def pos(self) -> list[float]:
        return [self.x, self.y]
    
    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font):
        angle = c_to_rad(self.angle)
        pygame.draw.line(screen, (0, 0, 0), (screen.get_width()/2 + 50*self.x - 20*math.cos(angle), screen.get_height()/2 + 50*self.y - 20*math.sin(angle)), (screen.get_width()/2 + 50*self.x + 20*math.cos(angle), screen.get_height()/2 + 50*self.y + 20*math.sin(angle)), 2)
        text_surface = font.render(f"{self.mirror_name}", True, (0, 0, 0))
        screen.blit(text_surface, (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y - 30))