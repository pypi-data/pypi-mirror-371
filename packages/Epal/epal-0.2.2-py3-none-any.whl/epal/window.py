import pygame
import warnings
from .entity.color import Color
from . import __globals__


class Window:
    def __init__(self, width : int, height : int, clear_color : Color = Color(0, 0, 0), max_fps : int = 60):
        if __globals__.__window__ != None:
            raise RuntimeError("You may only have one window existing at a time")

        self.width = width
        self.height = height
        self.clear_color = clear_color
        self.max_fps = max_fps
        self.title = "epal window"

        self.__prev_title__ = ""

        self.__clock__ = pygame.time.Clock()

        pygame.init()
        self.__window__ = pygame.display.set_mode((self.width, self.height))

        if not pygame.get_init():
            warnings.warn("Pygame is not properly initialized. Expect problems", RuntimeWarning)
        if not pygame.display.get_init():
            warnings.warn("pygame.display is not properly initialized.\n The window might not have intialized propetly. Expect problems", RuntimeWarning)

        __globals__.__window__ = self

    def __update__(self) -> float:
        if self.title != self.__prev_title__:
            pygame.display.set_caption(self.title)

        self.__window__.fill(self.clear_color.as_tuple())
        self.width, self.height = self.__window__.get_size()
        self.__prev_title__ = self.title
        
        return self.__clock__.tick(self.max_fps) / 1000

    def __del__(self):
        pygame.display.quit()
        self.__terminate__()
    
    def __refresh__(self):
        pygame.display.flip()
    
    def __terminate__(self):
        pygame.quit()

    def get_fps(self):
        return self.__clock__.get_fps()