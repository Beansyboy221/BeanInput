"""Controller bind registries and definitions."""

import typing

import pygame.joystick

from .. import binds


class Bind(binds.Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_BINDS.append(self)

    def poll(self, controller: pygame.joystick.Joystick):
        raise NotImplementedError


class Button(Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_BUTTONS.append(self)

    def poll(self, controller):
        return controller.get_button(self.poll_id)


class Axis(Bind):
    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_AXES.append(self)

    def poll(self, controller):
        return controller.get_axis(self.poll_id)


AVAILABLE_BINDS: list[Bind] = []
"""A registry of all loaded controller binds."""

AVAILABLE_BUTTONS: list[Button] = []
"""A registry of all loaded controller buttons."""

AVAILABLE_AXES: list[Axis] = []
"""A registry of all loaded controller axes."""

A = Button("A", pygame.CONTROLLER_BUTTON_A)
B = Button("B", pygame.CONTROLLER_BUTTON_B)
X = Button("X", pygame.CONTROLLER_BUTTON_X)
Y = Button("Y", pygame.CONTROLLER_BUTTON_Y)
DPAD_UP = Button("DPAD_UP", pygame.CONTROLLER_BUTTON_DPAD_UP)
DPAD_DOWN = Button("DPAD_DOWN", pygame.CONTROLLER_BUTTON_DPAD_DOWN)
DPAD_LEFT = Button("DPAD_LEFT", pygame.CONTROLLER_BUTTON_DPAD_LEFT)
DPAD_RIGHT = Button("DPAD_RIGHT", pygame.CONTROLLER_BUTTON_DPAD_RIGHT)
LB = Button("LB", pygame.CONTROLLER_BUTTON_LEFTSHOULDER)
RB = Button("RB", pygame.CONTROLLER_BUTTON_RIGHTSHOULDER)
LEFT_STICK = Button("LS", pygame.CONTROLLER_BUTTON_LEFTSTICK)
RIGHT_STICK = Button("RS", pygame.CONTROLLER_BUTTON_RIGHTSTICK)
BACK = Button("BACK", pygame.CONTROLLER_BUTTON_BACK)
START = Button("START", pygame.CONTROLLER_BUTTON_START)

LT = Axis("LT", pygame.CONTROLLER_AXIS_TRIGGERLEFT)
RT = Axis("RT", pygame.CONTROLLER_AXIS_TRIGGERRIGHT)

LEFT_STICK_X = Axis("LX", pygame.CONTROLLER_AXIS_LEFTX)
LEFT_STICK_Y = Axis("LY", pygame.CONTROLLER_AXIS_LEFTY)
RIGHT_STICK_X = Axis("RX", pygame.CONTROLLER_AXIS_RIGHTX)
RIGHT_STICK_Y = Axis("RY", pygame.CONTROLLER_AXIS_RIGHTY)
