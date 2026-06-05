# Usage Guide

## Installation

```bash
pip install beaninput
```

Requires Python 3.11+.

## Quick Start

```python
from beaninput import config, helpers
from beaninput.keyboard.binds import Keys
from beaninput.mouse import binds as mouse_binds
from beaninput.controller import binds as controller_binds

# Start device listeners
helpers.start_listeners()

# Create a poll configuration
poll_config = config.PollConfig(
    keyboard_whitelist=(Keys.W, Keys.A, Keys.S, Keys.D),
    mouse_whitelist=(
        mouse_binds.DIRECTION_X,
        mouse_binds.DIRECTION_Y,
        mouse_binds.VELOCITY,
    ),
    controller_whitelist=(
        controller_binds.LEFT_STICK_X,
        controller_binds.LEFT_STICK_Y,
        controller_binds.A,
        controller_binds.B,
    ),
    capture_binds=(mouse_binds.MOUSE_LEFT,),
)

# Poll while the left mouse button is held
try:
    while True:
        data = helpers.poll_if_capturing(poll_config)
        if data is not None:
            print(data)
finally:
    helpers.stop_listeners()
```

## PollConfig

The [`PollConfig`](../src/beaninput/config.py) model configures polling behavior.

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
| `polling_rate` | `int` | `60` | Software polling rate in Hz |
| `keyboard_whitelist` | `tuple[keyboard.binds.Bind, ...]` | `()` | Keyboard binds to poll |
| `mouse_whitelist` | `tuple[mouse.binds.Bind, ...]` | `()` | Mouse binds to poll |
| `controller_whitelist` | `tuple[controller.binds.Bind, ...]` | `()` | Controller binds to poll |
| `capture_binds` | `tuple[binds.Bind, ...]` | `(mouse.MOUSE_RIGHT,)` | Binds that enable data capture |
| `capture_bind_gate` | `GateCallable` | `any` | Gate function for capture binds |
| `ignore_empty_polls` | `bool` | `True` | Skip rows where all features are 0 |
| `reset_mouse_on_release` | `bool` | `True` | Reset mouse deltas when capture stops |

### KillBinds (mixin)

Use [`KillBindMixin`](../src/beaninput/config.py) to add kill-switch binds:

```python
class MyConfig(config.PollConfig, config.KillBindMixin):
    pass

cfg = MyConfig(
    keyboard_whitelist=(),
    mouse_whitelist=(),
    controller_whitelist=(),
    capture_binds=(),
    kill_binds=(Keys.ESC,),
)
```

## Helpers

The [`helpers`](../src/beaninput/helpers.py) module provides high-level polling functions:

- `is_active(bind)`: Check if a single bind is currently active
- `are_active(binds, gate=any)`: Check binds against a boolean gate
- `poll_if_capturing(poll_config)`: Poll all devices but only return data when capture binds are active

Each device has helpers exclusive to that device as well:

- [`beaninput/controller/helpers`](../src/beaninput/controller/helpers.py)
- [`beaninput/keyboard/helpers`](../src/beaninput/keyboard/helpers.py)
- [`beaninput/mouse/helpers`](../src/beaninput/mouse/helpers.py)

## Bind Registry

All loaded binds are automatically tracked:

```python
from beaninput.binds import AVAILABLE_BINDS
from beaninput.keyboard import binds as kb
from beaninput.mouse import binds as ms
from beaninput.controller import binds as ct

# All binds across devices
print(AVAILABLE_BINDS)

# Per-device registries
print(kb.AVAILABLE_BINDS)   # all keyboard binds
print(ms.AVAILABLE_BINDS)   # all mouse binds
print(ms.AVAILABLE_BUTTONS) # mouse buttons only
print(ms.AVAILABLE_MOVES)   # mouse movement binds only
print(ct.AVAILABLE_BINDS)   # all controller binds
print(ct.AVAILABLE_BUTTONS) # controller buttons only
print(ct.AVAILABLE_AXES)    # controller axes (triggers and sticks) only
```

## Controller

### Controller Binds

All controller binds are accessible via `beaninput.controller.binds`:

**Buttons:** `A`, `B`, `X`, `Y`, `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `LB`, `RB`, `LEFT_STICK`, `RIGHT_STICK`, `BACK`, `START`

**Axes:** `LT`, `RT`, `LEFT_STICK_X`, `LEFT_STICK_Y`, `RIGHT_STICK_X`, `RIGHT_STICK_Y`

Controller support uses `pygame.joystick`. Call `beaninput.controller.helpers.start()` to detect and cache controllers.

## Keyboard

### Keybinds

All keybinds are accessible via `beaninput.keyboard.binds.Keys`:

- **Letters**: `A` through `Z`
- **Digits**: `ZERO` through `NINE`
- **Symbols**: `PLUS`, `MINUS`, `ASTERISK`, `SLASH`, `DOT`, `COMMA`, `SPACE_KEY`, etc.
- **Control**: `ENTER`, `ESC`, `BACKSPACE`, `TAB`, `SPACE`, `CAPS_LOCK`, `NUM_LOCK`, `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`, `INSERT`, `DELETE`
- **Arrows**: `UP`, `DOWN`, `LEFT`, `RIGHT`
- **Modifiers**: `CTRL`, `ALT`, `SHIFT`, `CMD`, and left/right variants
- **Function**: `F1` through `F20`

Keyboard binds use `pynput` listeners under the hood. A background listener tracks pressed/released keys.

Start the listener before polling:

```python
from beaninput.keyboard import helpers

helpers.start_listener()
```

Stop it when done:

```python
helpers.stop_listener()
```

## Mouse

### Mouse Binds

All mouse binds are accessible via `beaninput.mouse.binds`:

- **Buttons**: `MOUSE_LEFT`, `MOUSE_RIGHT`, `MOUSE_MIDDLE`, `MOUSE_4`, `MOUSE_5` (MOUSE_4+ are Windows exclusive)
- **Movement**: `DIRECTION_X`, `DIRECTION_Y`, `VELOCITY`
Direction gives normalized delta per axis. Velocity is `log(1 + magnitude)` of the mouse delta.

Mouse polling combines button state (via `pynput` listener) with raw delta tracking via a platform-specific listener (`RawMouseListener`). Supported platforms: Windows, macOS, Linux.

Start the listeners before polling:

```python
from beaninput.mouse import helpers

helpers.start_listeners()
```

Stop them when done:

```python
helpers.stop_listeners()
```
