"""Parse OpenGL enum definitions required by feature levels."""

from copy import copy
from typing import Optional, Iterable, Sequence
import xml.etree.ElementTree as xml

import attr

from gladiator.optional import OptionalValue
from gladiator.resources import read_resource_file


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Type:
    """OpenGL type containing a low-level and potentially a high-level type."""

    low_level: str
    high_level: Optional[str]
    front_modifiers: Optional[str]
    back_modifiers: Optional[str]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Parameter:
    """An OpenGL command parameter."""

    name: str
    type_: Type
    length: Optional[str]  #: length or parameter name


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Command:
    """An OpenGL command."""

    name: str
    return_type: Type
    params: Iterable[Parameter]


def _parse_front_modifiers(node: xml.Element, ptype: xml.Element):
    fragments = tuple(node.itertext())
    ptype_index = fragments.index(ptype.text)
    return " ".join(fragments[0:ptype_index]).strip()


def _strip_name_tag(param: xml.Element):
    param = copy(param)
    name_node = param.find("name")
    if name_node is not None:
        param.remove(name_node)
    return param


_KNOWN_LOW_LEVEL_TYPES = [
    t for t in read_resource_file("data/low_level_types").split("\n") if t
]


def _locate_type(fragments: Sequence[str]):
    for index, fragment in enumerate(fragments):
        if fragment in _KNOWN_LOW_LEVEL_TYPES:
            return index
    return -1


def _parse_unnamed_type(param: xml.Element):
    # if the ptype tag is missing, we cannot identify modifiers, so we try
    # locate the base type within the whole string from a list of known
    # low-level types and infer modifiers knowing the type's location
    fragments = "".join(t.strip() for t in param.itertext()).split(" ")
    type_index = _locate_type(fragments)
    if type_index == -1:
        return " ".join(fragments), None, None

    return (
        fragments[type_index],
        " ".join(fragments[:type_index]),
        " ".join(fragments[(type_index + 1) :]),
    )


def _parse_named_type(param: xml.Element, ptype: xml.Element):
    return (
        ptype.text.strip(),
        _parse_front_modifiers(param, ptype),
        ptype.tail,
    )


def _parse_type(param: xml.Element):
    param = _strip_name_tag(param)
    ptype = param.find("ptype")
    if ptype is not None:
        low_level, fmod, bmod = _parse_named_type(param, ptype)
    else:
        low_level, fmod, bmod = _parse_unnamed_type(param)

    return Type(
        low_level=low_level,
        high_level=param.attrib.get("group"),
        front_modifiers=OptionalValue(fmod).map(lambda t: t.strip()).truthy_or_none,
        back_modifiers=OptionalValue(bmod).map(lambda t: t.strip()).truthy_or_none,
    )


def _parse_name(node: xml.Element):
    return OptionalValue(node.find("name")).map(lambda n: n.text).value


def _parse_prototype(node: xml.Element):
    return _parse_name(node), _parse_type(node)


def _parse_parameters(command_node: xml.Element):
    for node in command_node:
        if node.tag == "param":
            yield Parameter(
                name=OptionalValue(node.find("name")).map(lambda n: n.text).value,
                type_=_parse_type(node),
                length=node.attrib.get("len"),
            )


def parse_command(node: xml.Element):
    """Parse the given command node."""
    name, return_type = _parse_prototype(OptionalValue(node.find("proto")).value)
    return Command(
        name=name, return_type=return_type, params=tuple(_parse_parameters(node))
    )


def parse_required_commands(
    required_commands: Iterable[str],
    container_node: xml.Element,
):
    """Parse all required commands and yield their names, parameters and return types."""
    for node in container_node:
        if _parse_name(OptionalValue(node.find("proto")).value) in required_commands:
            yield parse_command(node)
