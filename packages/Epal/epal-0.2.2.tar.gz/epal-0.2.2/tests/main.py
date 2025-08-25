import epal




class SceneSwitcher(epal.Component):
    def __init__(self, parent, scene : epal.Scene | None = None):
        super().__init__(parent)

        self.scene_to_switch_too : epal.Scene = scene

    def update(self):
        if epal.Input.IsKeyPressed(epal.KeyCode.Return):
            epal.Application.set_active_scene(self.scene_to_switch_too)
    
class PlayerController(epal.Component):
    def __init__(self, parent, speed : float = 10, slipperieness : float = 0.6):
        super().__init__(parent)

        self.require_component(epal.Transform)
        self.speed : float = speed
        self.slipperieness : float = slipperieness
        self.velocity : epal.Vector2 = epal.Vector2(0, 0)
    
    def update(self):
        transform = self.parent.get_component(epal.Transform)
        
        if epal.Input.IsKeyHeld(epal.Input.GetKeyCode("s")):
            self.velocity.y += self.speed * epal.Application.get_delta_time()
        
        if epal.Input.IsKeyHeld(epal.Input.GetKeyCode("w")):
            self.velocity.y -= self.speed * epal.Application.get_delta_time()

        if epal.Input.IsKeyHeld(epal.Input.GetKeyCode("d")):
            self.velocity.x += self.speed * epal.Application.get_delta_time()
        
        if epal.Input.IsKeyHeld(epal.Input.GetKeyCode("a")):
            self.velocity.x -= self.speed * epal.Application.get_delta_time()

        transform.position += self.velocity
        self.velocity *= self.slipperieness
class AudioController(epal.Component):
    def __init__(self, parent):
        super().__init__(parent)

        self.require_component(epal.AudioPlayer)
    
    def update(self):
        if epal.Input.IsKeyPressed(epal.KeyCode.Space):
            self.parent.get_component(epal.AudioPlayer).toggle()
class Layerer(epal.Component):
    def __init__(self, parent):
        super().__init__(parent)

        self.require_component(epal.Rect)
    
    def awake(self):
        rect = self.parent.get_component(epal.Rect)
        rect.color = epal.Color(255, 101, 120)
        self.parent.get_component(epal.Transform).scale = epal.Vector2(100, 100)

    def update(self):
        if epal.Input.IsKeyPressed(epal.KeyCode.Tab):
            if self.parent.layer == 2:
                self.parent.layer = 0
            elif self.parent.layer == 0:
                self.parent.layer = 2

if __name__ == "__main__":
    window = epal.Window(1080, 720, epal.Color(255, 255, 255))
    app = epal.Application(window)

    assets = epal.AssetManager.load_asset_pack("test.eap")

    main_scene = epal.Scene()
    scene_2 = epal.Scene()

    image = epal.Entity(layer = 1)
    image.add_component(epal.Image, asset = assets.get_asset("Dog"))
    image.get_component(epal.Transform).scale = epal.Vector2(100, 100)
    
    img2 = image.instantiate()
    img2.layer = 0
    
    image.add_component(PlayerController, speed = 100, slipperieness = 0.8)
    image.add_component(SceneSwitcher, scene = scene_2)


    audio = epal.Entity()
    audio.add_component(AudioController)
    
    audio.get_component(epal.AudioPlayer).add_clip(assets.get_asset("Green Sky"))

    text = epal.Entity(scene = scene_2, layer = 1)
    layerer = epal.Entity(scene = scene_2, layer = 2)
    text.add_component(epal.Text, text = "Hello, This is scene 2")
    text.add_component(SceneSwitcher, scene = main_scene)

    layerer.add_component(Layerer)

    app.run()