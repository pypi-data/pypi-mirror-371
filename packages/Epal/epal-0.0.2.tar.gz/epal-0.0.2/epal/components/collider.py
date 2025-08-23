from .component import Component
from .transform import Transform

from .. import application as app

import pygame

class Collider(Component):
    def __init__(self, parent):
        super().__init__(parent)

        self.require_component(Transform)
        self.colliding = False
        self.colliding_with : app.Entity = None
    
    def update(self):
        scene = app.Application.get_active_scene()
        transform = self.parent.get_component(Transform)
        entities = scene.get_all_entities()

        entities = list(filter(lambda entity: (entity.has_component(Collider) and entity != self.parent), entities))

        rects = []
        for e in entities:
            trans : Transform = e.get_component(Transform)
            rects.append(pygame.Rect(*trans.as_rect()))
        col = pygame.Rect.collidelist(pygame.Rect(*transform.as_rect()), rects)

        if col != -1: 
            self.colliding = True
            self.colliding_with = entities[col]
        else:
            self.colliding = False
            self.colliding_with = None

        