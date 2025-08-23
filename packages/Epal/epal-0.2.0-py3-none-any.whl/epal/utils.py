from typing import Self
import os

try: os.remove("epal_runtime.log")
except FileNotFoundError: pass

from  . import config

class Vector2:
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def __add__(self, other) -> Self:
        return Vector2(self.x + other.x, self.y + other.y)
    def __sub__(self, other) -> Self:
        return Vector2(self.x - other.x, self.y - other.y)
    def __mul__(self, other) -> Self:
        return Vector2(self.x * other, self.y * other)
    def __div__(self, other) -> Self:
        return Vector2(self.x / other, self.y / other)

class EpalLogger:
    def __init__(self, name : str):
        self.name = name
        
        if config.do_log:
            try:
                self.file = open("epal_runtime.log", "a")
            except FileNotFoundError:
                self.file = open("epal_runtime.log", "w")
    
    def log(self, msg : str):
        if config.do_log:
            self.file.write(f"[{self.name}]: {msg}\n")
            self.file.flush()

    def __del__(self):
        if config.do_log:
            self.file.close()
