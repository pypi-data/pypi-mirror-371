from typing import Type, Self, TypeVar
from types import MethodType
import warnings

from .. import __globals__
from ..components import component
from ..scene import Scene
from ..utils import EpalLogger


class Entity:
    def __init__(self, scene : Scene | None = None, components : list[Type[component.Component]] = [], layer : int = 0, **kwargs):
        if scene == None:
            __globals__.__application__.active_scene.add_entity(self)
            self.__scene__ = __globals__.__application__.active_scene
        else:
            scene.add_entity(self)
            self.__scene__ = scene

        self.enabled : bool = True
        self.layer : int = layer

        self.__components__ : list[component.Component] = []
        self.__comp_types__ : list[Type[component.Component]] = []
        self.__auto_comps__ : list[Type[component.Component]] = []

        self.__logger__ = EpalLogger(f"[scene_{self.__scene__.get_uuid()}]{type(self).__name__}_{self.__scene__.get_all_entities().index(self)}")

        for key, value in kwargs.items():
            if key not in dir(self):
                setattr(self, key, value)

        for comp in components:
            self.add_component(comp)

    def __awake__(self):
        for component in self.__components__:
            component.awake()

    def __update__(self):
        for component in self.__components__:
            component.update()

    def add_component(self, component : Type[component.Component], **kwargs) -> None:
        if not self.has_component(component):
            self.__logger__.log(f"Adding component '{component.__name__}'")
            self.__components__.append(component(self, **kwargs))
            self.__comp_types__.append(component)
        else:
            warnings.warn(f"Instance of '{type(self).__name__}' already has component '{component.__name__}'", RuntimeWarning, stacklevel=2)
    
    ComponentTypeVar = TypeVar("ComponentTypeVar")
    def get_component(self, t : Type[ComponentTypeVar]) -> ComponentTypeVar:
        for comp in self.__components__:
            if type(comp) == t:
                return comp
        
        raise AttributeError(f"Instance of '{type(self).__name__}' does not have component '{t.__name__}'")
    
    def has_component(self, component : Type[component.Component]) -> bool:
        for comp in self.__comp_types__:
            if comp == component:
                return True
        return False
    
    def remove_component(self, component : Type[component.Component]):
        if self.has_component(component):
            self.__components__.pop(self.__components__.index(self.get_component(component)))
            self.__comp_types__.pop(self.__comp_types__.index(component))
    
    def instantiate(self, scene : Scene | None = None) -> Self:
        attrs = {}
        for attr in dir(self): 
            if type(getattr(self, attr)) != MethodType: attrs[attr] = getattr(self, attr)

        comps : list[Type[component.Component]] = []
        for comp in self.__comp_types__:
            if comp not in self.__auto_comps__:
                comps.append(comp)


        if scene == None:
            e = Entity(scene = self.__scene__, components = comps, **attrs)
        else:
            e =  Entity(scene = scene, components = comps, **attrs)
        
        for comp in self.__components__:
            for attr in dir(comp):
                c = self.get_component(type(comp))

                if getattr(c, attr).__class__.__module__ != "builtins" and attr != "parent":
                    setattr(e.get_component(type(comp)), attr, getattr(self.get_component(type(comp)), attr))

        return e