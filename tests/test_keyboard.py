"""Tests for src.keyboard.helpers: keyboard listener and polling logic."""

import pytest

from beaninput.keyboard import helpers, binds


@pytest.fixture(autouse=True)
def auto_clean_active_binds():
    helpers.active_keybinds.clear()
    yield


class TestPollKeyboard:
    def test_returns_dict_of_bools(self):
        result = helpers.poll_keyboard((binds.Keys.A, binds.Keys.B))
        assert isinstance(result, dict)
        assert len(result) == 2
        assert all(isinstance(value, bool) for value in result.values())

    def test_empty_whitelist(self):
        assert helpers.poll_keyboard(()) == {}

    def test_active_bind_returns_true(self):
        helpers.active_keybinds.add(binds.Keys.W)
        whitelist = (binds.Keys.W, binds.Keys.A)
        result = helpers.poll_keyboard(whitelist)
        assert result[binds.Keys.W] is True
        assert result[binds.Keys.A] is False
        helpers.active_keybinds.discard(binds.Keys.W)
