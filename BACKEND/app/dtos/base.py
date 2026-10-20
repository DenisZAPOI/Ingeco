"""
Base models of every DTO.

Python uses snake_case, the JSON uses camelCase. These classes do the
translation, and it is the only place where it happens: neither controllers nor
services handle a camelCase key.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_core import PydanticCustomError

from ..utils.errors import BUSINESS_RULE_ERROR

Value = TypeVar("Value")
Cleaned = TypeVar("Cleaned")


def apply_rule(rule: Callable[[Value], Cleaned], value: Value) -> Cleaned:
    """Runs a rule of services/ inside a field validator.

    The rule's French message becomes the field's message in the 400 response,
    shown as is next to the field.
    """
    try:
        return rule(value)
    except ValueError as error:
        raise field_error(str(error)) from None


def field_error(message: str) -> PydanticCustomError:
    """A field error with our own French message, to raise in a validator."""
    return PydanticCustomError(BUSINESS_RULE_ERROR, message)


class ApiModel(BaseModel):
    """Fields in snake_case in Python, in camelCase in the JSON."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def to_json(self) -> dict:
        # mode="json": dates in ISO 8601 (Flask would write "Thu, 17 Sep 2026…").
        # A field without value is sent as null, not left out: the TypeScript
        # types generated from the OpenAPI schema expect every field.
        return self.model_dump(mode="json", by_alias=True)


class InputModel(ApiModel):
    """Request body: an unknown field is refused with a 400."""

    model_config = ConfigDict(extra="forbid")


class ErrorDto(ApiModel):
    """Single shape of errors. Declare it for every error code of a route:
    the documentation then lists all its errors, and so do the front types."""

    error: str = Field(examples=["Not Found"])
    detail: Any = Field(None, examples=["Ride not found."])
