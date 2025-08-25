import pygame

from .pulseprofile import PulseProfile

class Laser:
    def __init__(self, beam_profile: PulseProfile, dir: tuple, pos_cm2: tuple) -> None:
        self.beam = beam_profile
        assert len(dir) == 2 and len(pos_cm2) == 2
        self.dirx = dir[0]
        self.diry = dir[1]
        self.x = pos_cm2[0]
        self.y = pos_cm2[1]

    def pos(self) -> list[float]:
        return [self.x, self.y]
    
    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font):
        pygame.draw.circle(screen, (0, 0, 0), (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y), 10)
        text_surface = font.render("LASER", True, (0, 0, 0))
        screen.blit(text_surface, (screen.get_width()/2 + 50*self.x - 30, screen.get_height()/2 + 50*self.y - 30))