"""Test type definition parsing."""

import xml.etree.ElementTree as xml

from gladiator.parser.type import get_type_definitions


def test_parse_definitions(spec: xml.Element):
    for node in spec:
        if node.tag == "types":
            defs = tuple(t.statement for t in get_type_definitions(node))
            assert "typedef unsigned int GLenum;" in defs
            assert "#include <KHR/khrplatform.h>" not in defs
