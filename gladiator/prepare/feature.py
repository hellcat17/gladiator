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

    def __lt__(self, other):
        if isinstance(other, PreparedFeatureLevel):
            return self.version.major < other.version.major or (
                self.version.major == other.version.major
                and self.version.minor < other.version.minor
            )

        raise NotImplementedError()


def prepare_feature_levels(
    api: FeatureApi,
    requirements: Requirements,
    prepared_commands: Mapping[str, PreparedCommand],
) -> List[PreparedFeatureLevel]:
    """Assign commands to the features that first introduced them and link them
    to already prepared commands.
    """
    features: DefaultDict[Feature, List[PreparedCommand]] = defaultdict(list)

    for command, version in requirements.commands.items():
        feature = Feature(api=api, version=version)
        features[feature].append(prepared_commands[command])

    prepped: List[PreparedFeatureLevel] = []
    for feature, commands in features.items():
        prepped.append(
            PreparedFeatureLevel(
                api=feature.api, version=feature.version, commands=commands
            )
        )

    return sorted(prepped)
