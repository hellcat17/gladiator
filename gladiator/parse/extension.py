"""Parse OpenGL extension definitions."""

from typing import Iterable, Optional
import xml.etree.ElementTree as xml

import attr

from gladiator.parse.feature import (
    apply_requirements,
    FeatureApi,
    FeatureVersion,
    RequirementMapping,
)


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class SupportedApi:
    api: FeatureApi
    min_version: Optional[FeatureVersion] = None
    max_version: Optional[FeatureVersion] = None


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Extension:
    name: str
    supported_apis: Iterable[SupportedApi]
    required_enums: Iterable[str]
    required_commands: Iterable[str]


def _parse_supported_apis(node: xml.Element):
    for supported in node.attrib["supported"].split("|"):
        if supported == "glcore":
            yield SupportedApi(
                api=FeatureApi.GL, min_version=FeatureVersion(major=3, minor=1)
            )
        elif supported == "gl":
            yield SupportedApi(
                api=FeatureApi.GL, max_version=FeatureVersion(major=3, minor=0)
            )
        else:
            yield SupportedApi(api=FeatureApi.from_string(supported))


def parse_required_extensions(
    extensions_root: xml.Element, required_extensions: Iterable[str]
):
    """Parse all required extensions and yield their enums and commands."""
    for ext_node in extensions_root:
        name = ext_node.attrib["name"]
        if name in required_extensions:
            supported = tuple(_parse_supported_apis(ext_node))
            enums: RequirementMapping = {}
            commands: RequirementMapping = {}
            apply_requirements(
                ext_node, FeatureVersion(major=1, minor=0), enums, commands
            )

            yield Extension(
                name=name,
                supported_apis=supported,
                required_enums=tuple(enums.keys()),
                required_commands=tuple(commands.keys()),
            )
