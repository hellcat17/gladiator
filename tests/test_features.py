"""Test feature definition parsing."""

from typing import List
import xml.etree.ElementTree as xml

import pytest

from gladiator.parser.feature import (
    is_compatible,
    get_feature_requirements,
    Feature,
    FeatureApi,
    FeatureVersion,
)


@pytest.mark.parametrize(
    "feature,other_feature,result",
    [
        (
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3)),
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3)),
            True,
        ),
        (
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3)),
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=1, minor=1)),
            True,
        ),
        (
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3)),
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=4)),
            False,
        ),
        (
            Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3)),
            Feature(api=FeatureApi.GLES2, version=FeatureVersion(major=3, minor=1)),
            False,
        ),
        (
            Feature(api=FeatureApi.GLES1, version=FeatureVersion(major=1, minor=0)),
            Feature(api=FeatureApi.GLES2, version=FeatureVersion(major=2, minor=0)),
            False,
        ),
    ],
)
def test_is_compatible(feature, other_feature, result):
    assert is_compatible(feature, other_feature) == result


def _collect_features(spec: xml.Element):
    for node in spec:
        if node.tag == "feature":
            yield node


def test_parse_requirements(spec: xml.Element):
    candidates = tuple(_collect_features(spec))

    gl_1_1 = Feature(api=FeatureApi.GL, version=FeatureVersion(major=1, minor=1))
    requirements = get_feature_requirements(gl_1_1, candidates)
    assert "GL_CURRENT_BIT" in requirements.enums
    assert "glFrustum" in requirements.commands
    assert requirements.enums["GL_CURRENT_BIT"] == FeatureVersion(major=1, minor=0)
    assert requirements.commands["glFrustum"] == FeatureVersion(major=1, minor=0)

    gl_3_3 = Feature(api=FeatureApi.GL, version=FeatureVersion(major=3, minor=3))
    requirements = get_feature_requirements(gl_3_3, candidates)
    assert "GL_CURRENT_BIT" not in requirements.enums
    assert "glFrustum" not in requirements.commands
