# Epal -  A Entity component system (ECS) for pygame

Epal is a unity-like entity component system for python, based on pygame.
The ECS is based on this article: <https://en.wikipedia.org/wiki/Entity_component_system>

We all know that pygame can get pretty verbose on bigger projects, so the aim of Epal is to make it less verbose, while at the same time implementing an Entity component system (ECS)

## Demo
There is a demo attached to this project, the ```main.py``` file
As of epal version 0.0.2 the demo requires an epal asset pack, to generate the asset pack just run the ```generate_asset_pack.py``` file

## Usage

Epal has a pretty simple api, however there is a lot of boilerplate code to get out of the way. Since Epal is scene based, and a scene requires an application, a window, ready for entities, looks like this:
```python
from epal import *

# Initialize an epal window that fills with white
window = Window(1080, 720, clear_color = Color(255, 255, 255))
# Then we initialize a window
app = Application(window)

# Then a scene (It automatically gets added to the application)
main_scene = Scene()

# And then run the application (This starts the mainloop)
app.run()
```

Now, this looks like a lot of boilerplate code, and it is. However, once you have all this, adding an entity, is as easy as adding ```entity = Entity()``` if you do this however, you wont see anything on the screen, dont worry, the entity is there, there is just no renderer component added.
To do this, you add 
```python
from epal import *


...
# Create an entity
entity = Entity()
# Add a rectangle renderer component
entity.add_component(Rect)
```

# Components
## Component API
Since epal is an ECS (Entity component system) of course there are components. In epal components are the main way to interact with everything.

Before I can start explaining how to write components, I first have to explain what a component even is. In it's most basic form, a component is, in epal's case, a class that contains functions to manipulate the object it is attached to. This can go from as simple as storing positional data for the entity, to entire player controllers or advanced physics simulations.

An empty epal component would look like this:
```python
from epal import Component

class MyComponent(Component):
    # The constructor has to take in an argument, 'parent'
    # This argument is passed to the parent class so component in this case
    # The parent class constructor defines parent as a member variable to the component
    def __init__(self, parent):
        super().__init__(parent)
    
    # awake is called when the entity starts it's life (every time the scene gets switched to)
    def awake(self):
        pass

    # And update gets called every frame the parent entity is alive
    def update(self):
        pass
```

A component gets added to an entity via the member function ``.add_component()`` this takes in the class typename, not an instance of the class, so for our example component it would be ``entity.add_component(MyComponent)``

If you have a component that relies on other components, there is a member function defined for every component ``self.require_component()``. The parameter is the same as ``add_component()``, but instead of blindly adding the component, which returns a warning if the component already is there, ``require_component()`` also checks if the component already is there.

If you want other constructor arguments for your component feel free to add them. To accsess them when you add an component, you can add as many keyword arguments as you want to ``add_component()``

# Asset manager
For assets, epal also got you covered, in epal there is an AssetManager class, this asset manager unifies all assets into one class, and makes it easy to get an asset from a name.

## Usage
Of course most classes in epal also allow non-epal assets, so paths or similar, but some epal classes require ```epal.Asset```'s, so its recommended to use the epal asset manager, especially on larger projects

Initializing a asset manager is as simple as this:
```python
import epal


...
# Initialize the asset manager
asset_manager = epal.AssetManager()
# Add a couple of assets to the manager
asset_manager.add_asset("Player", "./assets/player.png", epal.AssetType.Image)
asset_manager.add_asset("Menu theme", "./assets/main_menu_theme.mp3", epal.AssetType.Audio)
```

Currently Images and Audio are the only asset types supported, but that is due to change