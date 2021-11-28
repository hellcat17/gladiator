"""Gladiator's command-line interface."""

import sys
from typing import Dict, Sequence, Tuple
import xml.etree.ElementTree as xml

import attr

from gladiator.generate.code import generate_code
from gladiator.parse.enum import parse_required_enums
from gladiator.parse.command import parse_required_commands
from gladiator.parse.type import get_type_definitions, TypeDefinition
from gladiator.prepare.command import prepare_commands
from gladiator.prepare.enum import prepare_enums, PreparedEnum
from gladiator.prepare.feature import prepare_feature_levels, PreparedFeatureLevel
from gladiator.options import make_argument_parser, Options
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


def _get_all_requirements(spec_root: xml.Element, options: Options):
    feature_nodes = tuple(_get_feature_nodes(spec_root))
    for api, version in zip(options.api, options.version):
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


def _merge_requirements(
    requirements: Sequence[Tuple[Feature, Requirements]]
) -> Tuple[Feature, Requirements]:
    if len(requirements) == 1:
        return requirements[0][0], requirements[0][1]

    first = requirements[0][1]
    others = requirements[1:][1]
    return _MERGED_FEATURE, Requirements(
        enums=dict(_merge_enums(first, others)),
        commands=dict(_merge_commands(first, others)),
        is_merged=True,
    )


def _parse_definitions(spec_root: xml.Element, options: Options):
    types = enums = commands = ()
    enum_nodes = []  # NOTE: unfortunately, no common root
    feature, requirements = _merge_requirements(
        tuple(_get_all_requirements(spec_root, options))
    )

    for node in spec_root:
        if node.tag == "types":
            types = tuple(get_type_definitions(node))
        if node.tag == "enums":
            enum_nodes.append(node)
        if node.tag == "commands":
            commands = tuple(
                parse_required_commands(requirements.commands.keys(), node)
            )
        if node.tag == "extensions":
            pass  # TODO parse extensions

    enums = tuple(parse_required_enums(requirements.enums.keys(), enum_nodes))
    return types, enums, commands, feature, requirements


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class _ParseResult:
    types: Sequence[TypeDefinition]
    enums: Dict[str, PreparedEnum]
    feature_levels: Sequence[PreparedFeatureLevel]


def _parse_spec(spec_root: xml.Element, options: Options):
    types, enums, commands, feature, requirements = _parse_definitions(
        spec_root, options
    )
    prepared_enums = dict(prepare_enums(enums, options))
    prepared_commands = dict(prepare_commands(commands, prepared_enums, options))
    return _ParseResult(
        types=types,
        enums=prepared_enums,
        feature_levels=prepare_feature_levels(
            feature.api, requirements, prepared_commands
        ),
    )


def _check_preconditions(options: Options):
    if len(options.api) != len(options.version):
        raise SystemExit("ERROR: Must specify a version for every API")


def cli(*args) -> int:
    """Public CLI."""
    parser = make_argument_parser()
    if len(args) == 0:
        parser.print_usage()
        return 1

    try:
        parsed_cli = parser.parse_args(args)
        options = Options(**(parsed_cli.__dict__))
        _check_preconditions(options)

        spec_root = xml.parse(options.spec_file).getroot()
        result = _parse_spec(spec_root, options)
        generate_code(
            options, result.types, result.enums.values(), result.feature_levels
        )

        return 0
    except SystemExit as exc:
        return exc.code


if __name__ == "__main__":
    sys.exit(cli(*sys.argv[1:]))
