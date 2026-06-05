"""Raw mouse listener for macOS (Quartz)."""

import logging

import Quartz

from . import base

logger = logging.getLogger("beaninput")

_MOUSE_MOVE_MASK = (
    (1 << Quartz.kCGEventMouseMoved)
    | (1 << Quartz.kCGEventLeftMouseDragged)
    | (1 << Quartz.kCGEventRightMouseDragged)
    | (1 << Quartz.kCGEventOtherMouseDragged)
)


class RawMouseListener(base.BaseMouseListener):
    def __init__(self):
        super().__init__()
        self._run_loop = None
        self._tap = None
        self._source = None

    def _event_callback(self, proxy, type_, event, refcon):
        delta_x = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGMouseEventDeltaX)
        delta_y = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGMouseEventDeltaY)
        with self._lock:
            self._delta_x += delta_x
            self._delta_y += delta_y
        return event

    def _run(self):
        self._tap = Quartz.CGEventTapCreate(
            Quartz.kCGHIDEventTap,
            Quartz.kCGEventTapOptionListenOnly,
            Quartz.kCGEventTapOptionDefault,
            _MOUSE_MOVE_MASK,
            self._event_callback,
            None,
        )
        if not self._tap:
            logger.warning(
                "macOS event tap creation failed — mouse movement will not be tracked. "
                "Grant Accessibility permissions in System Settings > Privacy & Security."
            )
            return

        Quartz.CGEventTapEnable(self._tap, True)
        self._run_loop = Quartz.CFRunLoopGetCurrent()
        self._source = Quartz.CFMachPortCreateRunLoopSource(None, self._tap, 0)
        Quartz.CFRunLoopAddSource(
            self._run_loop, self._source, Quartz.kCFRunLoopCommonModes
        )
        self.running = True
        Quartz.CFRunLoopRun()
        self.running = False

    def stop(self):
        if self._tap:
            Quartz.CGEventTapEnable(self._tap, False)
            Quartz.CFMachPortInvalidate(self._tap)
        if self._source and self._run_loop:
            Quartz.CFRunLoopRemoveSource(
                self._run_loop, self._source, Quartz.kCFRunLoopCommonModes
            )
        if self._run_loop:
            Quartz.CFRunLoopStop(self._run_loop)
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
