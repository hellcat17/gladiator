"""Test preparing commands and enums."""

import xml.etree.ElementTree as xml

import pytest

from gladiator.parse.enum import parse_required_enums
from gladiator.parse.command import parse_required_commands
from gladiator.prepare.enum import prepare_enums
from gladiator.prepare.command import prepare_commands, CommandType, CastAction


def _get_enum_nodes(spec: xml.Element):
    for node in spec:
        if node.tag == "enums":
            yield node


def test_prepare_enum(spec: xml.Element):
    candidates = tuple(_get_enum_nodes(spec))
    clbuf_mask = next(parse_required_enums(["GL_DEPTH_BUFFER_BIT"], candidates))
    clbuf_mask = next(prepare_enums([clbuf_mask]))[1]

    assert clbuf_mask.is_bitmask
    assert "0x00000100" in [e.value for e in clbuf_mask.values]


def _get_commands_root(spec: xml.Element):
    for node in spec:
        if node.tag == "commands":
            return node

    pytest.fail("commands root not found in OpenGL spec")


def test_prepare_command(spec: xml.Element):
    candidates = tuple(_get_enum_nodes(spec))
    enums = tuple(parse_required_enums(["GL_DEPTH_BUFFER_BIT"], candidates))
    enums = dict(prepare_enums(enums))
    commands = tuple(parse_required_commands(["glClear"], _get_commands_root(spec)))
    gl_clear = dict(prepare_commands(commands, enums))["glClear"]

    assert gl_clear.type_ == CommandType.DEFAULT
    assert gl_clear.implementation.return_type.low_level == "void"
    assert next(iter(gl_clear.implementation.param_conversions)).action.param == "mask"
    assert (
        next(iter(gl_clear.implementation.param_conversions)).action.to.high_level
        == enums["ClearBufferMask"]
    )
    assert (
        next(iter(gl_clear.implementation.params)).type_.high_level
        == enums["ClearBufferMask"]
    )
