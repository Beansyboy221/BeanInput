"""Raw mouse listener for Linux (evdev)."""

import threading
import logging
import select

import evdev

from . import base

logger = logging.getLogger("beaninput")


class RawMouseListener(base.BaseMouseListener):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    @staticmethod
    def _find_mouse(devices):
        """Pick the best mouse device from a list of input devices."""
        # Prefer devices with both relative movement and button support
        candidates = [
            device
            for device in devices
            if evdev.ecodes.EV_REL in device.capabilities()
            and evdev.ecodes.EV_KEY in device.capabilities()
        ]
        # Exclude absolute-position devices (touchpads, tablets)
        pure = [
            device
            for device in candidates
            if evdev.ecodes.EV_ABS not in device.capabilities()
        ]
        if pure:
            return pure[0]
        if candidates:
            return candidates[0]
        # Fall back to any device with relative movement
        fallback = [
            device for device in devices if evdev.ecodes.EV_REL in device.capabilities()
        ]
        return fallback[0] if fallback else None

    def _run(self):
        paths = evdev.list_devices()
        if not paths:
            logger.warning(
                "No input devices found — mouse movement will not be tracked."
            )
            return

        devices = [evdev.InputDevice(path) for path in paths]
        mouse_device = None
        try:
            mouse_device = self._find_mouse(devices)
            if not mouse_device:
                logger.warning(
                    "No mouse device found — mouse movement will not be tracked."
                )
                return

            logger.info("Tracking mouse: %s (%s)", mouse_device.name, mouse_device.path)

            mouse_device.grab()

            self.running = True
            while not self._stop_event.is_set():
                r, _, _ = select.select([mouse_device.fd], [], [], 0.01)
                if r:
                    for event in mouse_device.read():
                        if event.type == evdev.ecodes.EV_REL:
                            with self._lock:
                                if event.code == evdev.ecodes.REL_X:
                                    self._delta_x += event.value
                                elif event.code == evdev.ecodes.REL_Y:
                                    self._delta_y += event.value
        except OSError as e:
            logger.error("Failed to access input device: %s", e)
        finally:
            self.running = False
            if mouse_device:
                try:
                    mouse_device.ungrab()
                except Exception:
                    pass
                mouse_device.close()
            for device in devices:
                if device is not mouse_device:
                    device.close()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
