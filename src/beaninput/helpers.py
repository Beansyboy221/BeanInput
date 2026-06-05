"""Universal polling functions."""

from .controller import helpers as controller_helpers, binds as controller_binds
from .keyboard import helpers as keyboard_helpers, binds as keyboard_binds
from .mouse import helpers as mouse_helpers

from . import config
from . import binds

# This file needs to be as optimized as possible.


def start_listeners():
    """Starts all device listeners (keyboard, mouse, controller)."""
    keyboard_helpers.start_listener()
    mouse_helpers.start_listeners()
    controller_helpers.start()


def stop_listeners():
    """Stops all device listeners (keyboard, mouse)."""
    keyboard_helpers.stop_listener()
    mouse_helpers.stop_listeners()


def is_active(bind: binds.Bind) -> bool:
    """Determines whether a bind is active."""
    if isinstance(bind, controller_binds.Bind):
        return controller_helpers.is_active(bind)
    if isinstance(bind, keyboard_binds.Bind):
        return keyboard_helpers.is_active(bind)
    else:
        return mouse_helpers.is_active(bind)


def are_active(binds: set[binds.Bind], gate: config.GateCallable = any) -> bool:
    """Determines whether a set of binds are active based on the provided gate."""
    return gate([is_active(bind) for bind in binds])


def poll_if_capturing(
    poll_params: config.PollConfig,
) -> dict[binds.Bind, bool | float | int] | None:
    """Polls input devices if capture bind(s) are active."""
    if not (
        poll_params.keyboard_whitelist
        or poll_params.mouse_whitelist
        or poll_params.controller_whitelist
    ):
        return None

    capturing = are_active(poll_params.capture_binds, poll_params.capture_bind_gate)
    if not capturing:
        if poll_params.reset_mouse_on_release:
            mouse_helpers.mouse_move_listener.reset_deltas()
        return None

    poll = {}
    poll.update(controller_helpers.poll_controller(poll_params.controller_whitelist))
    poll.update(keyboard_helpers.poll_keyboard(poll_params.keyboard_whitelist))
    poll.update(mouse_helpers.poll_mouse(poll_params.mouse_whitelist))
    if poll_params.ignore_empty_polls and not any(poll.values()):
        return None

    return poll
