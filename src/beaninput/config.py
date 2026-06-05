"""Parameters required for polling logic."""

import pydantic
import typing

from .controller import binds as controller_binds
from .keyboard import binds as keyboard_binds
from .mouse import binds as mouse_binds
from . import binds

GateCallable = typing.Callable[[typing.Iterable[bool]], bool]
"""A function that acts as a boolean gate."""


class PollConfig(pydantic.BaseModel):
    """Parameters needed for polling data."""

    polling_rate: int = pydantic.Field(
        default=60,
        description="The polling rate used when polling the data (not the hardware polling rate).",
    )
    """The polling rate used when polling the data (not the hardware polling rate)."""

    keyboard_whitelist: tuple[keyboard_binds.Bind, ...] = pydantic.Field(
        default_factory=tuple,
        description="A set of keyboard input features to poll for.",
    )
    """A set of keyboard input features to poll for."""

    mouse_whitelist: tuple[mouse_binds.Bind, ...] = pydantic.Field(
        default_factory=tuple,
        description="A set of mouse input features to poll for.",
    )
    """A set of mouse input features to poll for."""

    controller_whitelist: tuple[controller_binds.Bind, ...] = pydantic.Field(
        default_factory=tuple,
        description="A set of controller input features to poll for.",
    )
    """A set of controller input features to poll for."""

    capture_binds: tuple[binds.Bind, ...] = pydantic.Field(
        default_factory=lambda: (mouse_binds.MOUSE_RIGHT,),
        description="A set of binds that enable data capturing when activated.",
    )
    """A set of binds that enable data capturing when activated."""

    capture_bind_gate: GateCallable = pydantic.Field(
        default=any,
        description="Whether any or all of the capture binds must be active to enable capturing.",
    )
    """Whether any or all of the capture binds must be active to enable capturing."""

    ignore_empty_polls: bool = pydantic.Field(
        default=True,
        description="Whether or not empty rows of features should be written to the data.",
    )
    """Whether or not empty rows of features should be written to the data."""

    reset_mouse_on_release: bool = pydantic.Field(
        default=True,
        description="Whether or not mouse deltas are set to 0 when the capture bind is released.",
    )
    """Whether or not mouse deltas are set to 0 when the capture bind is released."""

    @property
    def whitelist(self) -> tuple[binds.Bind, ...]:
        """All device whitelists combined."""
        return (
            *self.keyboard_whitelist,
            *self.mouse_whitelist,
            *self.controller_whitelist,
        )

    @property
    def features_per_poll(self) -> int:
        """The number of features in each poll (row)."""
        return len(self.whitelist)

    @pydantic.model_validator(mode="after")
    def validate_no_duplicates(self) -> typing.Self:
        if len(self.whitelist) != len(set(self.whitelist)):
            raise ValueError(f"Duplicate binds found in whitelist.")
        return self

    @pydantic.model_validator(mode="after")
    def validate_capture_binds(self) -> typing.Self:
        if conflicts := set(self.whitelist) & set(self.capture_binds):
            raise ValueError(f"Capture binds found in whitelist: {conflicts}")
        return self

    @pydantic.model_validator(mode="after")
    def validate_whitelist_not_empty(self) -> typing.Self:
        if not self.whitelist:
            raise ValueError("At least one whitelist must contain at least one bind.")
        return self


class KillBindMixin(pydantic.BaseModel):
    """Adds kill bind configs."""

    kill_binds: tuple[binds.Bind, ...] = pydantic.Field(
        description="A set of binds that stop the program when activated."
    )
    """A set of binds that stop the program when activated."""

    kill_bind_logic: GateCallable = pydantic.Field(
        default=any,
        description="Whether any or all of the kill binds must be held to stop.",
    )
    """Whether any or all of the kill binds must be held to stop."""
