"""Tests for src.helpers: high-level polling functions."""

from unittest.mock import patch

from beaninput import helpers, config
from beaninput.controller import (
    helpers as controller_helpers,
    binds as controller_binds,
)
from beaninput.keyboard import helpers as keyboard_helpers, binds as keyboard_binds
from beaninput.mouse import helpers as mouse_helpers, binds as mouse_binds


class TestIsActive:
    def test_dispatches_to_keyboard(self):
        with patch.object(keyboard_helpers, "is_active", return_value=True):
            assert helpers.is_active(keyboard_binds.Keys.W) is True

    def test_dispatches_to_mouse(self):
        with patch.object(mouse_helpers, "is_active", return_value=True):
            assert helpers.is_active(mouse_binds.MOUSE_LEFT) is True

    def test_dispatches_to_controller(self):
        with patch.object(controller_helpers, "is_active", return_value=True):
            assert helpers.is_active(controller_binds.A) is True


class TestAreActive:
    def test_builtin_gates(self):
        whitelist = (keyboard_binds.Keys.A, keyboard_binds.Keys.B)
        with patch.object(helpers, "is_active", side_effect=[True, True, True, True]):
            assert helpers.are_active(whitelist) is True
            assert helpers.are_active(whitelist, gate=all) is True
        with patch.object(helpers, "is_active", side_effect=[True, False, True, False]):
            assert helpers.are_active(whitelist) is True
            assert helpers.are_active(whitelist, gate=all) is False
        with patch.object(
            helpers, "is_active", side_effect=[False, False, False, False]
        ):
            assert helpers.are_active(whitelist) is False
            assert helpers.are_active(whitelist, gate=all) is False


class TestPollIfCapturing:
    poll_config = config.PollConfig(
        keyboard_whitelist=(keyboard_binds.Keys.W,),
        mouse_whitelist=(),
        controller_whitelist=(),
        capture_binds=(keyboard_binds.Keys.SPACE,),
    )

    def test_returns_none_when_whitelist_empty(self):
        empty_config = config.PollConfig(
            keyboard_whitelist=(keyboard_binds.Keys.W,),
            mouse_whitelist=(),
            controller_whitelist=(),
            capture_binds=(keyboard_binds.Keys.SPACE,),
        )
        empty_config.keyboard_whitelist = ()
        assert helpers.poll_if_capturing(empty_config) is None

    def test_returns_none_when_not_capturing(self):
        with (
            patch.object(helpers, "are_active", return_value=False),
            patch.object(mouse_helpers, "mouse_move_listener") as mock_listener,
        ):
            assert helpers.poll_if_capturing(self.poll_config) is None
            mock_listener.reset_deltas.assert_called_once()

    def test_returns_poll_when_capturing(self):
        with (
            patch.object(helpers, "are_active", return_value=True),
            patch.object(
                keyboard_helpers, "poll_keyboard", return_value={keyboard_binds.Keys.W: True}
            ),
            patch.object(mouse_helpers, "poll_mouse", return_value={}),
            patch.object(controller_helpers, "poll_controller", return_value={}),
        ):
            assert helpers.poll_if_capturing(self.poll_config) == {keyboard_binds.Keys.W: True}

    def test_ignores_empty_polls(self):
        with (
            patch.object(helpers, "are_active", return_value=True),
            patch.object(
                keyboard_helpers,
                "poll_keyboard",
                return_value={keyboard_binds.Keys.W: False},
            ),
            patch.object(mouse_helpers, "poll_mouse", return_value={}),
            patch.object(controller_helpers, "poll_controller", return_value={}),
        ):
            assert helpers.poll_if_capturing(self.poll_config) is None

    def test_does_not_reset_mouse_deltas_when_capturing(self):
        with (
            patch.object(helpers, "are_active", return_value=True),
            patch.object(
                keyboard_helpers,
                "poll_keyboard",
                return_value={keyboard_binds.Keys.W: False},
            ),
            patch.object(mouse_helpers, "poll_mouse", return_value={}),
            patch.object(controller_helpers, "poll_controller", return_value={}),
            patch.object(
                mouse_helpers.mouse_move_listener, "reset_deltas"
            ) as mock_reset,
        ):
            helpers.poll_if_capturing(self.poll_config)
            mock_reset.assert_not_called()
