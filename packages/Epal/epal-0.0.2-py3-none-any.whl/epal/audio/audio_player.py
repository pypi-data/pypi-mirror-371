from ..asset_manager import Asset, AssetType
from ..components import Component

from .. import application

import pygame
import warnings

class AudioError(Exception):
    def __init__(self, *args: object) -> None:
        pass

class AudioWarning(Warning):
    def __init__(self, *args: object) -> None:
        pass

def get_free_audio_channel() -> int:
    used_ids = []
    for entity in application.Application.get_active_scene().get_all_entities():
        if entity.has_component(AudioPlayer):
            used_ids.append(entity.get_component(AudioPlayer).channel_id)

    for channel in range(0, pygame.mixer.get_num_channels()):
        if channel not in used_ids:
            return channel

    raise AudioError("No more free channels are available")

def stop_all_audio():
    for entity in application.Application.get_active_scene().get_all_entities():
        if entity.has_component(AudioPlayer):
            entity.get_component(AudioPlayer).stop()


class AudioPlayer(Component):
    def __init__(self, parent):
        super().__init__(parent)
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.clips : list[Asset] = []

        self.playing = False
        self.track : str = ""

        self.channel_id = get_free_audio_channel()
        self.__channel__ = pygame.mixer.Channel(self.channel_id)

        self.__idx__ = 0

    def awake(self):
        if len(self.clips):
            if self.track == "": self.track = self.clips[self.__idx__].name

    def add_clip(self, clip : Asset | str):
        if type(clip) == Asset:
            self.clips.append(clip)
        if type(clip) == str:
            a = Asset(clip, clip, AssetType.Audio)
            a.load()
            self.clips.append(a)

    def play_track(self, track : str):
        self.track = track
        try:
            self.__channel__.play(next((x for x in self.clips if x.name == self.track), None).get())
        except AttributeError:
            warnings.warn(f"Cannot play the track '{track}', it is not added to this AudioPlayer", AudioWarning, 2)

    #TODO: Remove __stack_level__ parameter. Its just a HACK
    def play(self, __stack_level__ : int = 2):
        if self.track != "":
            self.playing = True
            if self.__channel__.get_busy():
                self.__channel__.unpause()
            else:
                self.__channel__.play(next((x for x in self.clips if x.name == self.track), None).get())
        else:
            warnings.warn("Audio player has no tracks to play", AudioWarning, __stack_level__)

    def next(self):
        self.track = self.clips[self.idx+1].name
        self.idx += 1

    def pause(self):
        self.playing = False
        self.__channel__.pause()
    
    def stop(self):
        self.playing = False
        self.__channel__.stop()

    def fadeout(self, time : int):
        self.__channel__.fadeout(time)
        self.playing = False
    
    def toggle(self):
        if self.playing: self.pause()
        elif not self.playing: self.play(3)

def get_song_in_channel(channel : int) -> AudioPlayer:
    for entity in application.Application.get_active_scene().get_all_entities():
        if entity.has_component(AudioPlayer):
            if entity.get_component(AudioPlayer).channel_id == channel:
                return entity.get_component(AudioPlayer)
