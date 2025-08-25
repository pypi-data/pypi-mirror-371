from typing import Self


class Component:
    def __init__(self, parent):
        from ..entity import entity
        self.parent : entity.Entity = parent

    def awake(self):
        pass

    def update(self):
        pass

    def require_component(self, component : Self):
        if not self.parent.has_component(component):
            self.parent.add_component(component)
            self.parent.__auto_comps__.append(component)