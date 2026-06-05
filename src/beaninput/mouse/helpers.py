"""Mouse listener setup and polling functions."""

import platform
import math
import threading

import pynput

from .. import config
from . import binds

match platform.system():
    case "Windows":
        from .listeners import windows as raw_mouse
    case "Darwin":
        from .listeners import macos as raw_mouse
    case "Linux":
        from .listeners import linux as raw_mouse
    case _:
        raise RuntimeError(f"Unsupported platform: {platform.system()}")

# This file needs to be as optimized as possible.

_active_mouse_binds_lock = threading.Lock()
active_mouse_binds: set[binds.Button] = set()


def _on_click(x, y, button, pressed):
    with _active_mouse_binds_lock:
        if pressed:
            active_mouse_binds.add(button)
        else:
            active_mouse_binds.discard(button)


mouse_button_listener = pynput.mouse.Listener(
    on_click=_on_click,
)
mouse_move_listener = raw_mouse.RawMouseListener()


def start_listeners():
    """Starts all mouse listeners."""
    if not mouse_button_listener.running:
        mouse_button_listener.start()
    mouse_move_listener.start()


def stop_listeners():
    """Stops all mouse listeners."""
    mouse_button_listener.stop()
    mouse_move_listener.stop()


def poll_mouse(
    mouse_whitelist: tuple[binds.Bind, ...],
) -> dict[binds.Bind, bool | float]:
    """Returns a dict of bind states for mouse buttons and movement in the whitelist."""
    with _active_mouse_binds_lock:
        result = {bind: bind in active_mouse_binds for bind in mouse_whitelist}

    poll_direction_x = binds.DIRECTION_X in mouse_whitelist
    poll_direction_y = binds.DIRECTION_Y in mouse_whitelist
    poll_velocity = binds.VELOCITY in mouse_whitelist

    if poll_direction_x or poll_direction_y or poll_velocity:
        delta_x, delta_y = mouse_move_listener.get_deltas()
        mouse_move_listener.reset_deltas()
        magnitude = math.hypot(delta_x, delta_y)
        if poll_direction_x:
            result[binds.DIRECTION_X] = delta_x / magnitude if magnitude > 0 else 0.0
        if poll_direction_y:
            result[binds.DIRECTION_Y] = delta_y / magnitude if magnitude > 0 else 0.0
        if poll_velocity:
            result[binds.VELOCITY] = math.log1p(magnitude)
    return result


def is_active(bind: binds.Bind) -> bool:
    """Determines whether a bind is active."""
    with _active_mouse_binds_lock:
        return bind in active_mouse_binds


def are_active(binds: set[binds.Bind], gate: config.GateCallable = any) -> bool:
    """Determines whether a set of binds are active based on the provided gate."""
    return gate([is_active(bind) for bind in binds])
