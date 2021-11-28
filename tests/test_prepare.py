"""Test preparing commands and enums."""

from typing import List

import xml.etree.ElementTree as xml

import pytest
from gladiator.options import Options

from gladiator.parse.enum import parse_required_enums
from gladiator.parse.command import parse_required_commands
from gladiator.prepare.enum import prepare_enums
from gladiator.prepare.command import prepare_commands, CommandType
from gladiator.prepare.feature import prepare_feature_levels, PreparedFeatureLevel
from gladiator.parse.feature import (
    Feature,
    FeatureApi,
    FeatureVersion,
    get_feature_requirements,
)


def _get_enum_nodes(spec: xml.Element):
    for node in spec:
        if node.tag == "enums":
            yield node


def test_prepare_enum(spec: xml.Element):
    candidates = tuple(_get_enum_nodes(spec))
    clbuf_mask = next(parse_required_enums(["GL_DEPTH_BUFFER_BIT"], candidates))
    clbuf_mask = next(prepare_enums([clbuf_mask], Options()))[1]

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
    enums = dict(prepare_enums(enums, Options()))
    commands = tuple(parse_required_commands(["glClear"], _get_commands_root(spec)))
    gl_clear = dict(prepare_commands(commands, enums, Options()))["glClear"]

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


def _collect_features(spec: xml.Element):
    for node in spec:
        if node.tag == "feature":
            yield node


def _load_feature(feature, spec):
    f_nodes = tuple(_collect_features(spec))
    e_nodes = tuple(_get_enum_nodes(spec))
    c_root = _get_commands_root(spec)
    requirements = get_feature_requirements(feature, f_nodes)
    enums = tuple(parse_required_enums(tuple(requirements.enums.keys()), e_nodes))
    enums = dict(prepare_enums(enums, Options()))
    commands = tuple(
        parse_required_commands(tuple(requirements.commands.keys()), c_root)
    )
    commands = dict(prepare_commands(commands, enums, Options()))
    return prepare_feature_levels(feature.api, requirements, commands)


def _in_ascending_order(levels: List[PreparedFeatureLevel]):
    return all(levels[i] < levels[i + 1] for i in range(len(levels) - 1))


def test_prepare_feature(spec: xml.Element):
    gl_1_1 = Feature(api=FeatureApi.GL, version=FeatureVersion(major=1, minor=1))
    levels = _load_feature(gl_1_1, spec)
    assert _in_ascending_order(levels)
    # immediate mode still present when requesting a v1.1 profile
    lev_1_0 = next(l for l in levels if l.version.major == 1 and l.version.minor == 0)
    assert "glColor3f" in [c.original.name for c in lev_1_0.commands]

    gl_3_1 = Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=1))
    levels = _load_feature(gl_3_1, spec)
    # immediate mode not present anymore when requesting a v3.1 profile
    lev_3_1 = next(l for l in levels if l.version.major == 3 and l.version.minor == 1)
    assert "glColor3f" not in [c.original.name for c in lev_3_1.commands]
