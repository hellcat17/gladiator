"""Prepare OpenGL features for use in templates."""

from collections import defaultdict
from typing import DefaultDict, Iterable, List, Mapping

import attr

from gladiator.parse.feature import Feature, FeatureApi, FeatureVersion, Requirements
from gladiator.prepare.command import PreparedCommand


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class PreparedFeatureLevel:
    api: FeatureApi
    version: FeatureVersion
    commands: Iterable[PreparedCommand]
    is_merged: bool

    def __lt__(self, other):
        if isinstance(other, PreparedFeatureLevel):
            return self.version.major < other.version.major or (
                self.version.major == other.version.major
                and self.version.minor < other.version.minor
            )

        raise NotImplementedError()


def _determine_levels(
    api: FeatureApi,
    requirements: Requirements,
    prepared_commands: Mapping[str, PreparedCommand],
):
    levels: DefaultDict[Feature, List[PreparedCommand]] = defaultdict(list)
    for command, version in requirements.commands.items():
        feature = Feature(api=api, version=version)
        levels[feature].append(prepared_commands[command])
    return levels


def _prepare_levels(levels: Mapping[Feature, List[PreparedCommand]]):
    for feature, commands in levels.items():
        yield PreparedFeatureLevel(
            api=feature.api,
            version=feature.version,
            commands=commands,
            is_merged=False,
        )


def prepare_feature_levels(
    api: FeatureApi,
    requirements: Requirements,
    prepared_commands: Mapping[str, PreparedCommand],
) -> List[PreparedFeatureLevel]:
    """Assign commands to the features that first introduced them and link them
    to already prepared commands.
    """
    # we don't distinct between feature levels when multiple APIs were intersected
    if requirements.is_merged:
        return [
            PreparedFeatureLevel(
                api=api,
                version=FeatureVersion(major=0, minor=0),
                commands=prepared_commands.values(),
                is_merged=True,
            )
        ]

    return sorted(
        _prepare_levels(_determine_levels(api, requirements, prepared_commands))
    )
