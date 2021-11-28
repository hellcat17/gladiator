"""Parse OpenGL enum definitions required by feature levels."""

from collections import defaultdict
from typing import Dict, Iterable, List
import xml.etree.ElementTree as xml

import attr

from gladiator.optional import OptionalValue


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class EnumValue:
    name: str
    value: str


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Enum:
    name: str
    is_bitmask: bool
    values: Iterable[EnumValue]


def _parse_groups(node: xml.Element):
    return (
        OptionalValue(node.attrib.get("group"))
        .map(lambda v: v.split(","))
        .or_else([])
        .value
    )


def _parse_value(value_node: xml.Element):
    return EnumValue(name=value_node.attrib["name"], value=value_node.attrib["value"])


def _is_eligible(value_node: xml.Element, required_enums: Iterable[str]):
    return (
        value_node.attrib.get("name") in required_enums
        and value_node.attrib.get("type") != "ull"
    )


def _add_value_to_groups(value_node: xml.Element, result: Dict[str, List[EnumValue]]):
    value = _parse_value(value_node)
    for declared_group in _parse_groups(value_node):
        result[declared_group].append(value)


def parse_required_enums(
    required_enums: Iterable[str],
    enums: Iterable[xml.Element],
):
    """Parse all required enums and yield their names and values."""
    result: Dict[str, List[EnumValue]] = defaultdict(list)
    found_bitmasks: List[str] = []

    for enum_node in enums:
        group = enum_node.attrib.get("group")
        if enum_node.attrib.get("type") == "bitmask" and group:
            found_bitmasks.append(group)

        for value_node in enum_node:
            if _is_eligible(value_node, required_enums):
                _add_value_to_groups(value_node, result)

    for group, values in result.items():
        yield Enum(name=group, is_bitmask=(group in found_bitmasks), values=values)
