"""Parse OpenGL enum definitions required by feature levels."""

from collections import defaultdict
from typing import Iterable, Mapping
import xml.etree.ElementTree as xml

import attr


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
    return node.attrib["group"].split(",") if "group" in node.attrib else None


def _map_enums_to_groups(
    nodes: Iterable[xml.Element], required_enums: Iterable[str]
) -> Mapping[str, Iterable[xml.Element]]:
    result = defaultdict(list)

    for enum_node in nodes:
        group = enum_node.attrib.get("group")

        for value_node in enum_node:
            if value_node.attrib.get("name") in required_enums:
                groups = _parse_groups(value_node) or ([group] if group else [])
                for declared_group in groups:
                    result[declared_group].append(value_node)

    return result


def _parse_value(value_node: xml.Element):
    return EnumValue(name=value_node.attrib["name"], value=value_node.attrib["value"])


def _parse_enum(node: xml.Element, groups: Mapping[str, Iterable[xml.Element]]):
    name = node.attrib["group"]
    type_ = node.attrib.get("type")
    values = tuple(_parse_value(value) for value in groups[name])
    return Enum(name=name, is_bitmask=(type_ == "bitmask"), values=values)


def parse_required_enums(
    required_enums: Iterable[str],
    enums: Iterable[xml.Element],
):
    """Parse all required enums and yield their names and values."""
    groups = _map_enums_to_groups(enums, required_enums)
    for node in enums:
        if node.attrib.get("group") in groups:
            yield _parse_enum(node, groups)
