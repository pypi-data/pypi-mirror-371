from .component import Component
from ..utils import Vector2


class Transform(Component):
    def __init__(self, parent):
        super().__init__(parent)

        self.position : Vector2 = Vector2(0,0)
        self.scale : Vector2 = Vector2(10, 10)
    
    def as_rect(self) -> tuple[int, int, int, int]:
        return (self.position.x, self.position.y, self.scale.x, self.scale.y)