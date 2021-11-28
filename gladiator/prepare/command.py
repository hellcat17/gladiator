"""Prepare OpenGL commands for use in templates."""

from enum import auto, Enum
from typing import Iterable, Mapping, Optional, Union

import attr

from gladiator.parse.command import Command, Type
from gladiator.prepare.enum import PreparedEnum
from gladiator.prepare.style import transform_symbol
from gladiator.optional import OptionalValue
from gladiator.options import Options
from gladiator.resources import read_resource_file


class CommandType(Enum):
    DEFAULT = auto()
    GENERATOR = auto()
    DELETER = auto()


class ConversionType(Enum):
    CAST = auto()
    METHOD_CALL = auto()


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class TypeReference:
    low_level: str
    high_level: Optional[PreparedEnum]
    front_modifiers: Optional[str]
    back_modifiers: Optional[str]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedParameter:
    type_: TypeReference
    name: str


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class CastAction:
    param: str
    to: TypeReference


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class MethodCallAction:
    param: str
    method: str
    args: Iterable[str]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedConversion:
    type_: ConversionType
    action: Union[CastAction, MethodCallAction]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedImplementation:
    return_type: TypeReference
    params: Iterable[PreparedParameter]
    retval_conversion: PreparedConversion
    param_conversions: Iterable[PreparedConversion]
    retval_temporary = "retval"


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedCommand:
    original: Command
    name: str
    type_: CommandType
    implementation: PreparedImplementation


_TYPE_TRANSLATIONS = dict(
    t.split(",") for t in read_resource_file("data/type_translations").split("\n") if t
)


def _translate_low_level_type(low_level: str):
    return _TYPE_TRANSLATIONS.get(low_level, low_level)


def _make_type_reference(target: Type, prepared_enums: Mapping[str, PreparedEnum]):
    return TypeReference(
        low_level=_translate_low_level_type(target.low_level),
        front_modifiers=target.front_modifiers,
        back_modifiers=target.back_modifiers,
        high_level=OptionalValue(target.high_level)
        .map(prepared_enums.get)
        .value_or_none,
    )


def _make_default_implementation(
    command: Command, prepared_enums: Mapping[str, PreparedEnum]
):
    retval_typeref = _make_type_reference(command.return_type, prepared_enums)
    params_with_refs = [
        (param, _make_type_reference(param.type_, prepared_enums))
        for param in command.params
    ]

    return PreparedImplementation(
        return_type=retval_typeref,
        params=[
            PreparedParameter(type_=ref, name=param.name)
            for param, ref in params_with_refs
        ],
        retval_conversion=PreparedConversion(
            type_=ConversionType.CAST,
            action=CastAction(
                param=PreparedImplementation.retval_temporary, to=retval_typeref
            ),
        ),
        param_conversions=[
            PreparedConversion(
                type_=ConversionType.CAST, action=CastAction(param=param.name, to=ref)
            )
            for param, ref in params_with_refs
        ],
    )


# TODO: take options such as casing, style and namespace
# TODO: generate special wrappers for generators and deleters


def prepare_commands(
    commands: Iterable[Command],
    prepared_enums: Mapping[str, PreparedEnum],
    options: Options,
):
    """Prepare the given commands for use as references and in templates. The
    given enums are used to construct type references. Yields tuples mapping the
    original command name to the prepared command.
    """

    for command in commands:
        yield command.name, PreparedCommand(
            original=command,
            type_=CommandType.DEFAULT,
            implementation=_make_default_implementation(command, prepared_enums),
            name=transform_symbol(
                command.name, options.function_case, options.omit_prefix
            ),
        )
