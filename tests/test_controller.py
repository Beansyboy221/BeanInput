"""Tests for src.controller.helpers: controller polling logic."""

from unittest.mock import MagicMock, patch

import pytest

from beaninput.controller import helpers, binds


class TestGetController:
    def test_raises_when_no_controller(self):
        with patch.object(helpers, "_controller_cache", {}):
            with patch.object(helpers, "_update_controllers", return_value=None):
                with pytest.raises(RuntimeError):
                    helpers._get_controller(0)


class TestPollController:
    def test_polls_binds(self):
        mock_controller = MagicMock()
        mock_controller.get_button.side_effect = lambda id: id == binds.A.poll_id
        with patch.object(helpers, "_get_controller", return_value=mock_controller):
            whitelist = (binds.A, binds.B)
            result = helpers.poll_controller(whitelist)
            assert result[binds.A] is True
            assert result[binds.B] is False

    def test_polls_axis(self):
        mock_controller = MagicMock()
        mock_controller.get_axis.side_effect = lambda id: (
            0.5 if id == binds.LEFT_STICK_X.poll_id else -0.3
        )
        with patch.object(helpers, "_get_controller", return_value=mock_controller):
            whitelist = (binds.LEFT_STICK_X, binds.LEFT_STICK_Y)
            result = helpers.poll_controller(whitelist)
            assert result[binds.LEFT_STICK_X] == 0.5
            assert result[binds.LEFT_STICK_Y] == -0.3

    def test_empty_whitelist(self):
        with patch.object(helpers, "_get_controller", return_value=MagicMock()):
            assert helpers.poll_controller(()) == {}
