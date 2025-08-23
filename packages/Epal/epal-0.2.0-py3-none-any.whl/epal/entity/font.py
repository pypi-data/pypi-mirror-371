from typing import Union, Literal, Optional
import pygame
from .color import Color


class Font:
    def __init__(self, path : str = pygame.font.get_default_font(), size = 12):
        pygame.font.init()
        self.font = pygame.font.Font(path, size)
    def render(self, text: Union[str, bytes, None], antialias: bool | Literal[0] | Literal[1], color: Color, background: Optional[Color] = None):
        bg = background
        if background == None:
            bg = None
        else:
            bg = background.as_tuple()
        return self.font.render(text, antialias, color.as_tuple(), bg)