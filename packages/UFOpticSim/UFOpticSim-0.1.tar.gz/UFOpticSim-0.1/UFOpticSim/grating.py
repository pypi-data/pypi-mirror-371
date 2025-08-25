class Grating:
    def __init__(self, pos_cm2: tuple) -> None:
        self.x = pos_cm2[0]
        self.y = pos_cm2[1]

    def pos(self) -> list[float]:
        return [self.x, self.y]