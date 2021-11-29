"""Compare the features of multiple APIs and versions."""

from argparse import ArgumentParser
import sys
from typing import Iterable, Sequence, Tuple
import xml.etree.ElementTree as xml
from gladiator.options import add_feature_level_options

from gladiator.parse.feature import (
    Feature,
    FeatureApi,
    FeatureVersion,
    Requirements,
    get_feature_requirements,
    _parse_feature,
)

_MERGED_FEATURE = Feature(api=FeatureApi.GL, version=FeatureVersion(major=0, minor=0))


def _get_feature_nodes(spec_root: xml.Element):
    for node in spec_root:
        if node.tag == "feature":
            yield node


def _get_valid_features(feature_nodes):
    for node in feature_nodes:
        yield _parse_feature(node)


def _check_requirements(req, nodes, feature):
    if not req.enums or not req.commands:
        valid = ", ".join(str(f) for f in _get_valid_features(nodes))
        raise SystemExit(f"ERROR: {feature} does not exist in the spec. Valid: {valid}")


def get_all_feature_requirements(
    spec_root: xml.Element,
    apis: Iterable[FeatureApi],
    versions: Iterable[FeatureVersion],
):
    """Get all features and their requirements from the spec."""
    feature_nodes = tuple(_get_feature_nodes(spec_root))
    for api, version in zip(apis, versions):
        feature = Feature(api=api, version=version)
        requirements = get_feature_requirements(feature, feature_nodes)
        _check_requirements(requirements, feature_nodes, feature)
        yield feature, requirements


def _is_enum_shared(enum: str, requirements: Sequence[Requirements]):
    for req in requirements:
        if enum not in req.enums:
            return False
    return True


def _is_command_shared(cmd: str, requirements: Sequence[Requirements]):
    for req in requirements:
        if cmd not in req.commands:
            return False
    return True


def _merge_enums(first, others):
    for enum, level in first.enums.items():
        if _is_enum_shared(enum, others):
            yield enum, level


def _merge_commands(first, others):
    for cmd, level in first.commands.items():
        if _is_command_shared(cmd, others):
            yield cmd, level


def merge_requirements(
    requirements: Sequence[Tuple[Feature, Requirements]]
) -> Tuple[Feature, Requirements]:
    """Determine the lowest common denominator in the given requirements."""
    if len(requirements) == 1:
        return requirements[0][0], requirements[0][1]

    first = requirements[0][1]
    others = [t[1] for t in requirements[1:]]
    return _MERGED_FEATURE, Requirements(
        enums=dict(_merge_enums(first, others)),
        commands=dict(_merge_commands(first, others)),
        is_merged=True,
    )


def _make_argparser():
    parser = ArgumentParser(
        description="Determine the lowest common denominator across APIs and versions"
    )
    add_feature_level_options(parser)
    return parser


def _print_requirements(requirements: Requirements):
    print(f"Command intersection ({len(requirements.commands)})")
    print("----------------------------------")
    print("\n".join(requirements.commands.keys()))


def cli(*args) -> int:
    try:
        options = _make_argparser().parse_args(args)
    except SystemExit as exc:
        return exc.code

    spec = xml.parse(options.spec_file).getroot()
    reqs = tuple(get_all_feature_requirements(spec, options.api, options.version))
    _print_requirements(merge_requirements(reqs)[1])

    return 0


if __name__ == "__main__":
    sys.exit(cli(*sys.argv[1:]))
