"""Test enum definition parsing."""

from typing import Iterable
import xml.etree.ElementTree as xml

from gladiator.parser.enum import get_required_enums
from gladiator.parser.feature import (
    get_feature_requirements,
    Feature,
    FeatureApi,
    FeatureVersion,
)


TESTED_FEATURE = Feature(api=FeatureApi.GL, version=FeatureVersion(major=1, minor=0))


def _get_enum_nodes(spec: xml.Element):
    for node in spec:
        if node.tag == "enums":
            yield node


def _collect_features(spec: xml.Element):
    for node in spec:
        if node.tag == "feature":
            yield node


def _collect_required(spec: xml.Element):
    return tuple(
        get_feature_requirements(
            TESTED_FEATURE, tuple(_collect_features(spec))
        ).enums.keys()
    )


def test_parse_enums(spec: xml.Element):
    candidates = tuple(_get_enum_nodes(spec))
    all_enums = tuple(get_required_enums(_collect_required(spec), candidates))
    attrib_mask = next(e for e in all_enums if e.name == "AttribMask")
    clbuf_mask = next(e for e in all_enums if e.name == "ClearBufferMask")

    assert attrib_mask.is_bitmask
    assert (
        next(v for v in attrib_mask.values if v.name == "GL_CURRENT_BIT").value
        == "0x00000001"
    )
    assert (
        next(v for v in attrib_mask.values if v.name == "GL_ALL_ATTRIB_BITS").value
        == "0xFFFFFFFF"
    )
    assert (
        next(v for v in attrib_mask.values if v.name == "GL_DEPTH_BUFFER_BIT").value
        == "0x00000100"
    )

    assert clbuf_mask.is_bitmask
    assert (
        next(v for v in clbuf_mask.values if v.name == "GL_DEPTH_BUFFER_BIT").value
        == "0x00000100"
    )
