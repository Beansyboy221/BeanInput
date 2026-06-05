"""Tests for src.mouse.helpers: mouse listener setup and polling logic."""

from unittest.mock import MagicMock

import pytest

from beaninput.mouse import helpers, binds


@pytest.fixture(autouse=True)
def auto_clean_active_binds():
    helpers.active_mouse_binds.clear()
    yield


class TestPollMouse:
    def test_returns_dict_without_move_binds(self):
        result = helpers.poll_mouse((binds.MOUSE_LEFT, binds.MOUSE_RIGHT))
        assert isinstance(result, dict)
        assert len(result) == 2
        assert all(isinstance(value, bool) for value in result.values())

    def test_active_button_true(self):
        helpers.active_mouse_binds.add(binds.MOUSE_LEFT)
        whitelist = (binds.MOUSE_LEFT, binds.MOUSE_RIGHT)
        result = helpers.poll_mouse(whitelist)
        assert result[binds.MOUSE_LEFT] is True
        assert result[binds.MOUSE_RIGHT] is False

    def test_resets_deltas_after_poll(self):
        helpers.mouse_move_listener.get_deltas = MagicMock(return_value=(5.0, 3.0))
        helpers.mouse_move_listener.reset_deltas = MagicMock()
        result = helpers.poll_mouse((binds.DIRECTION_X,))
        helpers.mouse_move_listener.reset_deltas.assert_called_once()
        assert 0 < result[binds.DIRECTION_X] <= 1.0

    def test_directions_with_delta(self):
        helpers.mouse_move_listener.get_deltas = MagicMock(return_value=(3.0, 4.0))
        helpers.mouse_move_listener.reset_deltas = MagicMock()
        result = helpers.poll_mouse(
            (binds.DIRECTION_X, binds.DIRECTION_Y, binds.VELOCITY)
        )
        assert result[binds.DIRECTION_X] == pytest.approx(0.6)
        assert result[binds.DIRECTION_Y] == pytest.approx(0.8)
        assert result[binds.VELOCITY] == pytest.approx(1.791759469228055)

    def test_directions_with_no_delta(self):
        helpers.mouse_move_listener.get_deltas = MagicMock(return_value=(0.0, 0.0))
        helpers.mouse_move_listener.reset_deltas = MagicMock()
        result = helpers.poll_mouse(
            (binds.DIRECTION_X, binds.DIRECTION_Y, binds.VELOCITY)
        )
        assert result[binds.DIRECTION_X] == 0.0
        assert result[binds.DIRECTION_Y] == 0.0
        assert result[binds.VELOCITY] == 0.0

    def test_empty_whitelist(self):
        assert helpers.poll_mouse(()) == {}
