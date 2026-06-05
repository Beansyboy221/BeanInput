"""Mouse bind registries and definitions."""

import typing
import sys

import pynput

from .. import binds


class Bind(binds.Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_BINDS.append(self)


class Button(Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_BUTTONS.append(self)


class Move(Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_MOVES.append(self)


AVAILABLE_BINDS: list[Bind] = []
"""A registry of all loaded mouse binds."""

AVAILABLE_BUTTONS: list[Button] = []
"""A registry of all loaded mouse buttons."""

AVAILABLE_MOVES: list[Move] = []
"""A registry of all loaded mouse movement binds."""


MOUSE_LEFT = Button("LEFT_MOUSE", pynput.mouse.Button.left)
MOUSE_RIGHT = Button("RIGHT_MOUSE", pynput.mouse.Button.right)
MOUSE_MIDDLE = Button("MIDDLE_MOUSE", pynput.mouse.Button.middle)
if sys.platform == "win32":
    MOUSE_4 = Button("MOUSE_4", pynput.mouse.Button.x1)
    MOUSE_5 = Button("MOUSE_5", pynput.mouse.Button.x2)

DIRECTION_X = Move("MOUSE_X", "direction_x")
DIRECTION_Y = Move("MOUSE_Y", "direction_y")
VELOCITY = Move("MOUSE_VELOCITY", "velocity")
