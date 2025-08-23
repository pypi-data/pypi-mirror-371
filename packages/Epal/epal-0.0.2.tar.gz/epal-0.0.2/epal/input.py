import pygame
import pygame.locals
from enum import Enum


class KeyCode(Enum):
    __keys__ = {"1":pygame.K_1, "2":pygame.K_2, "3":pygame.K_3, "4":pygame.K_4, "5":pygame.K_5,"6":pygame.K_6, "7":pygame.K_7, "8":pygame.K_8, "9":pygame.K_9, "0":pygame.K_0,
                "q":pygame.K_q, "w":pygame.K_w, "e":pygame.K_e, "r":pygame.K_r, "t":pygame.K_t, "y":pygame.K_y, "u":pygame.K_u, "i":pygame.K_i, "o":pygame.K_o, "p":pygame.K_p,
                "a":pygame.K_a, "s":pygame.K_s, "d":pygame.K_d, "f":pygame.K_f, "g":pygame.K_g, "h":pygame.K_h, "j":pygame.K_j, "k":pygame.K_k, "l":pygame.K_l,
                "z":pygame.K_z, "x":pygame.K_x, "c":pygame.K_c, "v":pygame.K_v, "b":pygame.K_b, "n":pygame.K_n, "m":pygame.K_m, ",":pygame.K_COMMA, ".":pygame.K_PERIOD,
                ";":pygame.K_SEMICOLON, ":":pygame.K_COLON, "+" : pygame.K_PLUS, "-" : pygame.K_MINUS}
    Return = pygame.K_RETURN
    LeftShift = pygame.K_LSHIFT
    RightShift = pygame.K_RSHIFT
    Tab = pygame.K_TAB
    CapsLock = pygame.K_CAPSLOCK
    Escape = pygame.K_ESCAPE
    Space = pygame.K_SPACE

    F1 = pygame.K_F1
    F2 = pygame.K_F2
    F3 = pygame.K_F3
    F4 = pygame.K_F4
    F5 = pygame.K_F5
    F6 = pygame.K_F6
    F7 = pygame.K_F7
    F8 = pygame.K_F8
    F9 = pygame.K_F9
    F10 = pygame.K_F10
    F11 = pygame.K_F11
    F12 = pygame.K_F12
    F13 = pygame.K_F13
    F14 = pygame.K_F14
    F15 = pygame.K_F15

    NumpadPlus = pygame.K_KP_PLUS
    NumpadMinus = pygame.K_KP_MINUS
    NumpadMultiply = pygame.K_KP_MULTIPLY
    NumpadDivide = pygame.K_KP_DIVIDE

    Numpad0 = pygame.K_KP0
    Numpad1 = pygame.K_KP1
    Numpad2 = pygame.K_KP2
    Numpad3 = pygame.K_KP3
    Numpad4 = pygame.K_KP4
    Numpad5 = pygame.K_KP5
    Numpad6 = pygame.K_KP6
    Numpad7 = pygame.K_KP7
    Numpad8 = pygame.K_KP8
    Numpad9 = pygame.K_KP9

    ArrowUp = pygame.K_UP
    ArrowDown = pygame.K_DOWN
    ArrowLeft = pygame.K_LEFT
    ArrowRight = pygame.K_RIGHT

class MouseButtons(Enum):
    Left = 1
    Middle = 2
    Right = 3

class KeyMods(Enum):
    Control = pygame.KMOD_CTRL
    Alt = pygame.KMOD_ALT
    Shift = pygame.KMOD_SHIFT

__quit_event__ = False
__pressed_key__ = None
__released_key__ = None
__mods__ = pygame.KMOD_NONE

def __check_events__():
    global __quit_event__, __pressed_key__, __released_key__, __mods__
    __pressed_key__ = None
    __released_key__ = None
    __mods__ = pygame.key.get_mods()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN: 
            __pressed_key__ = event.key
            __released_key__ = None

        if event.type == pygame.KEYUP:
            __pressed_key__ = None
            __released_key__ = event.key
        
        if event.type == pygame.QUIT: __quit_event__ = True
        else: __quit_event__ = False

class Input:
    def GetKeyCode(key : str) -> int:
        return KeyCode.__keys__[key]
    def GetKeyName(key : int) -> str:
        if key == None: return
        try:
            return list(KeyCode.__keys__.keys())[list(KeyCode.__keys__.values()).index(key)]
        except ValueError:
            return "{Non-ascii key}"
    
    def GetQuitEvent() -> bool:
        return __quit_event__

    def IsKeyPressed(key_code : int | KeyCode) -> bool:
        if type(key_code) == int:
            return __pressed_key__ == key_code
        elif type(key_code) == KeyCode:
            return __pressed_key__ == key_code.value

    def IsKeyReleased(key_code : int) -> bool:
        if type(key_code) == int:
            return __released_key__ == key_code
        elif type(key_code) == KeyCode:
            return __released_key__ == key_code.value

    def IsKeyHeld(key_code : int | KeyCode) -> bool:
        if type(key_code) == int:
            return pygame.key.get_pressed()[key_code]
        elif type(key_code) == KeyCode:
            return pygame.key.get_pressed()[key_code.value]

    def GetPressedKey() -> int:
        return __pressed_key__

    def GetReleasedKey() -> int:
        return __released_key__
    
    def GetModifier(kmod : int | KeyMods) -> bool:
        if type(kmod) == int:
            return __mods__ & kmod != 0
        if type(kmod) == KeyMods:
            return __mods__ & kmod.value != 0
        
    def GetMousePosition() -> tuple[int, int]:
        return pygame.mouse.set_pos()
    def IsMousePressed(button_id : int) -> bool:
        return pygame.mouse.get_pressed()