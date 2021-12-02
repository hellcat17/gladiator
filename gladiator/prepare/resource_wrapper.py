"""Prepare scoped resource wrappers for use in templates."""

from enum import auto, Enum
from typing import Iterable, Mapping, Union

import attr

from gladiator.options import Options
from gladiator.prepare.command import PreparedCommand, TypeReference
from gladiator.prepare.style import transform_symbol
from gladiator.resources import read_resource_file


class ResourceWrapperType(Enum):
    SINGLE = auto()
    MULTI = auto()


class _MultiWrapper:
    def __init__(self, create: str, delete: str, singular_name: str, plural_name: str):
        self.create = create
        self.delete = delete
        self.singular_name = singular_name
        self.plural_name = plural_name

    def style(self, options: Options):
        self.singular_name = transform_symbol(
            self.singular_name, options.enum_case, True
        )
        self.plural_name = transform_symbol(self.plural_name, options.enum_case, True)
        return self


class _SingleWrapper:
    def __init__(self, create: str, delete: str, name: str):
        self.create = create
        self.delete = delete
        self.name = name

    def style(self, options: Options):
        self.name = transform_symbol(self.name, options.enum_case, True)
        return self


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedResourceWrapper:
    type_: ResourceWrapperType
    create: PreparedCommand
    delete: PreparedCommand
    additional_param_types: Iterable[TypeReference]
    underlying: Union[_MultiWrapper, _SingleWrapper]


_MULTI_RESOURCE_WRAPPERS = [
    _MultiWrapper(*w.split(","))
    for w in read_resource_file("data/scoped_resources_multi").split("\n")
    if w
]


_SINGLE_RESOURCE_WRAPPERS = [
    _SingleWrapper(*w.split(","))
    for w in read_resource_file("data/scoped_resources_single").split("\n")
    if w
]


def prepare_resource_wrappers(
    commands: Mapping[str, PreparedCommand], options: Options
):
    """Prepare scoped resource wrappers for OpenGL objects."""
    for wrapper in _MULTI_RESOURCE_WRAPPERS:
        if wrapper.create in commands and wrapper.delete in commands:
            yield PreparedResourceWrapper(
                type_=ResourceWrapperType.MULTI,
                underlying=wrapper.style(options),
                create=commands[wrapper.create],
                delete=commands[wrapper.delete],
                additional_param_types=[
                    p.type_
                    for p in commands[wrapper.create].implementation.params[0:-2]
                ],
            )

    for wrapper in _SINGLE_RESOURCE_WRAPPERS:
        if wrapper.create in commands and wrapper.delete in commands:
            yield PreparedResourceWrapper(
                type_=ResourceWrapperType.SINGLE,
                underlying=wrapper.style(options),
                create=commands[wrapper.create],
                delete=commands[wrapper.delete],
                additional_param_types=[
                    p.type_ for p in commands[wrapper.create].implementation.params
                ],
            )
