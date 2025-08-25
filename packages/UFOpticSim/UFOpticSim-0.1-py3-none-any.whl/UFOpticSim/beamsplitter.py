from .material import Material

class BeamSplitter:
    def __init__(self, material: Material, angle_to_horizontal: float, pos_cm2: tuple) -> None:
        self.material = material