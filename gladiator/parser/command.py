"""Parse OpenGL enum definitions required by feature levels."""

from copy import copy
from typing import Optional, Iterable
import xml.etree.ElementTree as xml

import attr

from gladiator.optional import OptionalValue


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Type:
    """OpenGL type containing a low-level and a potential high-level type."""

    low_level: str
    high_level: str  #: if non-existent, equals low_level
    front_modifiers: Optional[str]
    back_modifiers: Optional[str]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Parameter:
    """An OpenGL command parameter."""

    name: str
    type_: Type


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


def _parse_type(node: xml.Element):
    # remove non-type elements in the type definition (e.g. <name> in proto/param)
    node = copy(node)
    name_node = node.find("name")
    if name_node is not None:
        node.remove(name_node)

    ptype = OptionalValue(node.find("ptype"))
    low_level = (
        ptype.map(lambda n: n.text).or_else("".join(node.itertext())).value.strip()
    )
    fmod = ptype.map(lambda n: _parse_front_modifiers(node, n)).truthy_or_none
    bmod = ptype.map(lambda n: n.tail).map(lambda t: t.strip()).truthy_or_none

    return Type(
        low_level=low_level,
        high_level=node.attrib.get("group") or low_level,
        front_modifiers=fmod,
        back_modifiers=bmod,
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
            )


def parse_command(node: xml.Element):
    """Parse the given command node."""
    name, return_type = _parse_prototype(OptionalValue(node.find("proto")).value)
    return Command(
        name=name, return_type=return_type, params=tuple(_parse_parameters(node))
    )


def parse_required_commands(
    container_node: xml.Element, required_commands: Iterable[str]
):
    """Parse all required commands and yield their names, parameters and return types."""
    for node in container_node:
        if _parse_name(OptionalValue(node.find("proto")).value) in required_commands:
            yield parse_command(node)
