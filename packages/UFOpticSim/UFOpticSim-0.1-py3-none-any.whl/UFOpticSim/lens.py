import pygame

from .material import Material

class Lens:
    def __init__(self, material: Material, focal_length_mm: float, pos_cm2: tuple, lens_name: str) -> None:
        self.focal_length_mm = focal_length_mm 
        self.material = material
        self.x = pos_cm2[0]
        self.y = pos_cm2[1]
        self.lens_name = lens_name

    def pos(self) -> list[float]:
        return [self.x, self.y]
    
    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font):
        pygame.draw.line(screen, (0, 0, 0), (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y - 20), (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y + 20), 2)
        text_surface = font.render(f"{self.lens_name}", True, (0, 0, 0))
        screen.blit(text_surface, (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y - 30))