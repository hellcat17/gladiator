"""Parse OpenGL type definitions. Basically to be copied as-is, since it's C code."""

import xml.etree.ElementTree as xml

import attr

from gladiator.optional import OptionalValue


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class TypeDefinition:
    name: str
    statement: str


def _get_name(node: xml.Element):
    return (
        OptionalValue(node.find("name"))
        .map(lambda n: n.text)
        .or_else(node.attrib.get("name"))  # e.g. #ifdef'd GlhandleARB
        .value
    )


def parse_type_definition(node: xml.Element):
    """Parse a single <type> definition."""
    return TypeDefinition(name=_get_name(node), statement="".join(node.itertext()))


def get_type_definitions(container_node: xml.Element):
    """Parse all OpenGL <type> definitions and yield them."""
    for node in container_node:
        if (
            node.attrib.get("name", None) != "khrplatform"
        ):  # NOTE: skip #include directive
            yield parse_type_definition(node)
