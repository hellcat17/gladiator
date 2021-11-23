"""Parse OpenGL type definitions. Basically to be copied as-is, since it's C code."""

import xml.etree.ElementTree as xml

import attr


@attr.s(auto_attribs=True, slots=True, frozen=True)
class TypeDefinition:
    statement: str


def parse_type_definition(node: xml.Element):
    """Parse a single <type> definition."""
    return TypeDefinition("".join(node.itertext()))


def generate_type_definitions(container_node: xml.Element):
    """Parse the given node's descendent <type> definitions and generate objects."""
    for node in container_node:
        if node.attrib.get("name", None) != "khrplatform":  # NOTE: skip #include directive
            yield parse_type_definition(node)
