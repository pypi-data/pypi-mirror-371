from .window import Window
from . import __globals__
from .input import Input, __check_events__, KeyMods, KeyCode
from random import random

from . import audio
from . import scene
from .entity import color
from .utils import EpalLogger

from pygame import font, SRCALPHA, surface, mixer

from .asset_manager import Asset

from tkinter import messagebox
import traceback


def MultilineTextRender(font_object : font.Font, text : str, color : color.Color, background : color.Color = color.Color(0,0,0,0)):
    lines = text.split("\n")
    surf = surface.Surface((font_object.render(max(lines, key = len), True, color.as_tuple(), background.as_tuple()).get_rect().width, font_object.render(lines[0], True, color.as_tuple(), background.as_tuple()).get_rect().height * len(lines)), SRCALPHA).convert_alpha()
    surf.fill(background.as_tuple())
    for line in lines:
        txt = font_object.render(line, True, color.as_tuple())
        height = txt.get_rect().height
        rect = txt.get_rect()
        rect.centery = height * lines.index(line) + (height / 2)

        surf.blit(txt, rect)
    return surf


class Application:
    def __init__(self, window : Window):
        if __globals__.__application__ != None:
            self.__terminated__ = True
            raise RuntimeError("You may only have one application existing at a time")

        self.window = window
        self.active_scene : scene.Scene | None = None
        self.delta_time : float = 0.0
        self.__running__ = False
        self.__terminated__ = False
        self.__scenes__ : list[scene.Scene] = []
        self.__draw_overlay__ : bool = False
        self.__logger__ = EpalLogger("Application")

        Asset.null = Asset("NULL")
        Asset.null.load()

        self.__logger__.log("Start!")
        if window == None:
            raise Exception("A rendering application is no where to be lazy, don't set window to 'None'")

        __globals__.__application__ = self
        print(f"Epal version {__globals__.VERSION}_{__globals__.VERSION_NAME} initialized. Have fun!")
        self.__logger__.log(f"Epal version {__globals__.VERSION}_{__globals__.VERSION_NAME} initialized. Have fun!")

    def __render_overlay__(self):
        t = f"FPS: {round(self.window.get_fps())}\nDelta time: {self.delta_time}\nEntities: {len(self.active_scene.__entities__)}\nepal version: {__globals__.VERSION}_{__globals__.VERSION_NAME}\nCurrent scene id: {self.active_scene.get_uuid()}\nNum scenes: {len(self.__scenes__)}\n\nMax audio channels: {mixer.get_num_channels()}"
        for channel in range(0, mixer.get_num_channels()):
            song = audio.get_song_in_channel(channel)
            if song != None: t+=f"\n  - Channel {channel}: '{song.track}' playing: {song.playing}"
            else: t+=f"\n  - Channel {channel}: No AudioPlayer for this channel"
        self.window.__window__.blit(MultilineTextRender(font.Font(size=30), t, color.Color(255, 255, 255), color.Color(100, 100, 100, 150)), (10, 10))

    def run(self):
        self.__logger__.log("Starting application mainloop")
        self.__running__ = True
        self.active_scene.__awake__()

        while self.__running__:
            try:
                __check_events__()
                self.delta_time = self.window.__update__()

                self.active_scene.__update__()

                if (Input.GetModifier(KeyMods.Alt) and Input.IsKeyPressed(KeyCode.F5)):
                    self.__draw_overlay__ = not self.__draw_overlay__

                if self.__draw_overlay__: self.__render_overlay__()
                self.window.__refresh__()
                if Input.GetQuitEvent():
                    self.terminate()
            except Exception as err:
                self.terminate()
                messagebox.showerror(f"A error occurred ({type(err).__name__})", traceback.format_exc())

    def terminate(self):
        print("Terminating epal application. See you soon!")
        self.__logger__.log("Terminating...")
        self.__running__ = False
        self.__terminated__ = True
        if self.window != None: self.window.__del__()

    def add_scene(self, scene):
        uuids = []
        for s in self.__scenes__:
            uuids.append(s.__uuid__)
        
        scene.__uuid__ = round(random() * 100000)
        while scene.__uuid__ in uuids:
            scene.__uuid__ = round(random() * 100000)

        self.__scenes__.append(scene)
        self.active_scene = self.__scenes__[0]

    def get_scene_by_id(self, uuid : int) -> scene.Scene:
        return next((x for x in self.__scenes__ if x.__uuid__ == uuid), None)

    def __del__(self):
        if not self.__terminated__:
            self.terminate()
    
    def get_active_scene() -> scene.Scene:
        return __globals__.__application__.active_scene

    def set_active_scene(scene : scene.Scene):
        audio.stop_all_audio()
        __globals__.__application__.active_scene = scene
        __globals__.__application__.active_scene.__awake__()

    def get_scene_by_id(uuid : int):
        for s in __globals__.__application__.__scenes__:
            if s.__uuid__ == uuid:
                return s

    def get_window():
        return __globals__.__window__
    
    def get_delta_time() -> float:
        return __globals__.__application__.delta_time