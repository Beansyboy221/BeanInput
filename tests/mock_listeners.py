"""Test fixtures and configuration."""

from unittest.mock import patch

import pytest

from beaninput.keyboard import helpers as keyboard_helpers
from beaninput.mouse import helpers as mouse_helpers


@pytest.fixture
def mock_pynput_keyboard():
    with patch.object(keyboard_helpers, "keyboard_listener") as mock:
        yield mock


@pytest.fixture
def mock_pynput_mouse():
    with patch.object(mouse_helpers, "mouse_button_listener") as mock:
        yield mock


@pytest.fixture
def mock_raw_mouse():
    with patch.object(mouse_helpers, "mouse_move_listener") as mock:
        yield mock
