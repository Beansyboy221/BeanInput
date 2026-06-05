"""Controller discovery, caching, and polling functions."""

import logging

import pygame.joystick

from .. import config
from . import binds

# This file needs to be as optimized as possible.

logger = logging.getLogger("beaninput")


def _update_controllers() -> None:
    """Checks for changes in connected controllers and updates the cache."""
    for index in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(index)
        joy.init()
        _controller_cache[index] = joy
        logger.info(
            f"Controller: {joy.get_name()} cached at index: {index}"
        )


_controller_cache: dict[int, pygame.joystick.Joystick] = {}


def start():
    """Initializes pygame and caches connected controllers."""
    pygame.joystick.init()
    _update_controllers()


def _get_controller(index: int = 0) -> pygame.joystick.Joystick:
    """Get or initialize a joystick instance for the given index."""
    if index not in _controller_cache:
        _update_controllers()
        if index not in _controller_cache:
            raise RuntimeError(f"No controller connected with index: {index}")
    return _controller_cache[index]


def poll_controller(
    controller_whitelist: tuple[binds.Bind, ...], index: int = 0
) -> dict[binds.Bind, bool | int]:
    """Returns a dict of bind states for all binds in the given whitelist."""
    controller = _get_controller(index)
    if not controller:
        return {bind: 0 for bind in controller_whitelist}
    return {bind: bind.poll(controller) for bind in controller_whitelist}


def is_active(bind: binds.Bind, index: int = 0) -> bool:
    """Determines whether a bind is active."""
    return bool(poll_controller([bind], index)[0])


def are_active(
    binds: set[binds.Bind],
    gate: config.GateCallable = any,
    index: int = 0,
) -> bool:
    """Determines whether a set of binds are active based on the provided gate."""
    return gate([is_active(bind, index) for bind in binds])
