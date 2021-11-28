"""Parse OpenGL feature definitions."""

from enum import Enum
from typing import MutableMapping, Iterable
import xml.etree.ElementTree as xml

import attr

from gladiator.mixins import StringToEnumMixin
from gladiator.optional import OptionalValue


class FeatureApi(StringToEnumMixin, Enum):
    """An OpenGL feature API."""

    GL = "gl"
    GLES1 = "gles1"
    GLES2 = "gles2"
    GLSC2 = "glsc2"


class InvalidVersion(Exception):
    """Cannot parse OpenGL feature version number."""

    def __init__(self, version: str):
        super().__init__(f"Cannot parse feature version '{version}'")


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True, str=False)
class FeatureVersion:
    """An OpenGL feature version."""

    major: int
    minor: int

    @classmethod
    def from_string(cls, value: str):
        try:
            components = value.split(".")
            return cls(major=int(components[0]), minor=int(components[1]))
        except (IndexError, ValueError) as exc:
            raise InvalidVersion(value) from exc

    def __str__(self):
        return f"{self.major}.{self.minor}"


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True, str=False)
class Feature:
    """An OpenGL feature."""

    api: FeatureApi
    version: FeatureVersion

    def __str__(self):
        return f"{self.api.value} {self.version}"


RequirementMapping = MutableMapping[str, FeatureVersion]


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Requirements:
    """Requirements of a feature level."""

    enums: RequirementMapping
    commands: RequirementMapping
    is_merged: bool = False


def is_compatible(feature: Feature, other: Feature):
    """Determines if two features are compatible with one another."""
    return feature.api == other.api and not (
        other.version.major > feature.version.major
        or (
            other.version.major == feature.version.major
            and other.version.minor > feature.version.minor
        )
    )


def _parse_feature(node: xml.Element):
    api = node.attrib.get("api")
    if api is None:
        return None

    version = node.attrib.get("number")
    if version is None:
        return None

    return Feature(
        api=FeatureApi.from_string(api), version=FeatureVersion.from_string(version)
    )


def _parse_name(node: xml.Element) -> str:
    return OptionalValue(node.attrib.get("name")).value


def apply_requirements(
    new_feature: xml.Element,
    version: FeatureVersion,
    current_enums: RequirementMapping,
    current_commands: RequirementMapping,
):
    """Apply requirements and removals of a new feature.

    For example, core OpenGL 3.1 removes the fixed function pipeline entirely
    but adds several other functions.
    """
    for type_ in new_feature:
        if type_.tag == "require":
            for requirement in type_:
                if requirement.tag == "enum":
                    current_enums[_parse_name(requirement)] = version
                elif requirement.tag == "command":
                    current_commands[_parse_name(requirement)] = version
        elif type_.tag == "remove":
            for remove in type_:
                if remove.tag == "enum":
                    del current_enums[_parse_name(remove)]
                elif remove.tag == "command":
                    del current_commands[_parse_name(remove)]


def get_feature_requirements(
    requested_feature: Feature, features_root: Iterable[xml.Element]
):
    """Get the aggregated enums and commands of all features that are compatible
    with the requested feature level. These enums and commands still contain the
    feature level they originally came from.
    """
    enums: RequirementMapping = {}
    commands: RequirementMapping = {}

    for feature_node in features_root:
        current_feature = _parse_feature(feature_node)
        if current_feature and is_compatible(requested_feature, current_feature):
            apply_requirements(feature_node, current_feature.version, enums, commands)

    return Requirements(enums=enums, commands=commands)
