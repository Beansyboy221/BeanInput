"""Base bind registry and definition."""

import pydantic
import typing


class Bind(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True, frozen=True)
    name: str
    poll_id: typing.Any

    def __init__(self, name: str, poll_id: typing.Any, *args, **kwargs):
        super().__init__(name=name, poll_id=poll_id, *args, **kwargs)
        AVAILABLE_BINDS.append(self)


AVAILABLE_BINDS: list[Bind] = []
"""A registry of all loaded binds."""
