import pygame

class Screen:
    def __init__(self, pos_cm2) -> None:
        self.x = pos_cm2[0]
        self.y = pos_cm2[1]

    def pos(self) -> list[float]:
        return [self.x, self.y]
    
    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font):
        pygame.draw.line(screen, (0, 0, 0), (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y - 10), (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y + 10), 2)
        pygame.draw.line(screen, (0, 0, 0), (screen.get_width()/2 + 50*self.x - 10, screen.get_height()/2 + 50*self.y), (screen.get_width()/2 + 50*self.x + 10, screen.get_height()/2 + 50*self.y), 2)
        text_surface = font.render("Screen", True, (0, 0, 0))
        screen.blit(text_surface, (screen.get_width()/2 + 50*self.x, screen.get_height()/2 + 50*self.y + 20))