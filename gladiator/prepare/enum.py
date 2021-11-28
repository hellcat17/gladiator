"""Prepare OpenGL enums for use in templates."""

from typing import Iterable

import attr

from gladiator.parse.enum import Enum
from gladiator.prepare.style import transform_symbol
from gladiator.options import Options


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedEnumValue:
    name: str
    value: str


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedEnum:
    original_name: str
    name: str
    is_bitmask: bool
    values: Iterable[PreparedEnumValue]


# TODO: take options such as casing, style and namespace


def prepare_enums(enums: Iterable[Enum], options: Options):
    """Prepare the given enums for use as references and in templates. Yields tuples
    mapping the original enum name to the prepared enum.
    """
    for enum in enums:
        yield enum.name, PreparedEnum(
            original_name=enum.name,
            name=transform_symbol(enum.name, options.enum_case, options.omit_prefix),
            is_bitmask=enum.is_bitmask,
            values=[
                PreparedEnumValue(
                    value=value.value,
                    name=transform_symbol(
                        value.name, options.enum_value_case, options.omit_prefix
                    ),
                )
                for value in enum.values
            ],
        )
