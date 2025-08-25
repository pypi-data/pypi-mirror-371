import pygame
from .component import Component

from .. import __globals__
from ..entity.font import Font
from ..entity.color import Color
from ..components.shapes import Transform

class Text(Component):
    def __init__(self, parent, text : str = "Text component"):
        super().__init__(parent)
        self.require_component(Transform)

        self.surface = pygame.Surface((0, 0))
        self.text : str = text
        self.font_object : Font = Font()
        self.color : Color = Color(0, 0, 0)
        self.background : Color = Color(255, 255, 255, 0)

    def update(self):
        lines = self.text.split("\n")
        transform = self.parent.get_component(Transform)
        self.surface = pygame.surface.Surface((self.font_object.render(max(lines, key = len), True, self.color, self.background).get_rect().width,
                                      self.font_object.render(lines[0], True, self.color, self.background).get_rect().height * len(lines)),
                                      pygame.SRCALPHA).convert_alpha()
        self.surface.fill(self.background.as_tuple())
        for line in lines:
            txt = self.font_object.render(line, True, self.color)
            height = txt.get_rect().height
            rect = txt.get_rect()
            rect.centery = height * lines.index(line) + (height / 2)

            self.surface.blit(txt, rect)

        rect = self.surface.get_rect()
        rect.topleft = transform.position.as_tuple()
        __globals__.__window__.__window__.blit(self.surface, rect)
