class Color:
    def __init__(self, r : int, g : int, b : int, a : int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    
    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)