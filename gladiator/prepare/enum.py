"""Prepare OpenGL enums for use in templates."""

from typing import Iterable

import attr

from gladiator.parse.enum import Enum


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedEnumValue:
    name: str
    value: str


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedEnum:
    name: str
    namespace: str
    is_bitmask: bool
    values: Iterable[PreparedEnumValue]


# TODO: take options such as casing, style and namespace


def prepare_enums(enums: Iterable[Enum]):
    """Prepare the given enums for use as references and in templates. Yields tuples
    mapping the original enum name to the prepared enum.
    """
    for enum in enums:
        yield enum.name, PreparedEnum(
            name=enum.name,
            namespace="gl",
            is_bitmask=enum.is_bitmask,
            values=[
                PreparedEnumValue(name=value.name, value=value.value)
                for value in enum.values
            ],
        )
