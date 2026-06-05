"""Keyboard listener and polling functions."""

import threading

import pynput

from .. import config
from . import binds

# This file needs to be as optimized as possible.

_active_keybinds_lock = threading.Lock()
active_keybinds: set[binds.Bind] = set()


def _on_press(key):
    with _active_keybinds_lock:
        active_keybinds.add(key)


def _on_release(key):
    with _active_keybinds_lock:
        active_keybinds.discard(key)


keyboard_listener = pynput.keyboard.Listener(
    on_press=_on_press,
    on_release=_on_release,
)


def start_listener():
    """Starts the keyboard listener."""
    if not keyboard_listener.running:
        keyboard_listener.start()


def stop_listener():
    """Stops the keyboard listener."""
    keyboard_listener.stop()


def poll_keyboard(keyboard_whitelist: tuple[binds.Bind, ...]) -> dict[binds.Bind, bool]:
    """Returns a dict of bind states for all binds in the given whitelist."""
    with _active_keybinds_lock:
        return {bind: bind in active_keybinds for bind in keyboard_whitelist}


def is_active(bind: binds.Bind) -> bool:
    """Determines whether a bind is active."""
    with _active_keybinds_lock:
        return bind in active_keybinds


def are_active(binds: set[binds.Bind], gate: config.GateCallable = any) -> bool:
    """Determines whether a set of binds are active based on the provided gate."""
    return gate([is_active(bind) for bind in binds])
