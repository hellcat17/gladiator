"""Gladiator's command-line interface."""

import sys
from typing import Dict, Sequence
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
from gladiator.tools.compare import get_all_feature_requirements, merge_requirements
from gladiator.prepare.resource_wrapper import (
    prepare_resource_wrappers,
    PreparedResourceWrapper,
)


def _get_required_groups_by_commands(commands):
    for command in commands:
        if command.return_type.high_level:
            yield command.return_type.high_level
        for param in command.params:
            if param.type_.high_level:
                yield param.type_.high_level


def _filter_unneeded_groups(enums, commands):
    # NOTE: <require> nodes name required low-level enum values, but not the
    # high level types, thus we need to remove unneeded groups that were
    # included due to re-use of an enum value
    required = set(_get_required_groups_by_commands(commands))
    return [e for e in enums if e.name in required]


def _parse_definitions(spec_root: xml.Element, options: Options):
    types = enums = commands = ()
    enum_nodes = []  # NOTE: unfortunately, no common root
    feature, requirements = merge_requirements(
        tuple(get_all_feature_requirements(spec_root, options.api, options.version))
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

    enums = _filter_unneeded_groups(
        parse_required_enums(requirements.enums.keys(), enum_nodes), commands
    )
    return types, enums, commands, feature, requirements


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class _ParseResult:
    types: Sequence[TypeDefinition]
    enums: Dict[str, PreparedEnum]
    feature_levels: Sequence[PreparedFeatureLevel]
    resource_wrappers: Sequence[PreparedResourceWrapper]


def _parse_spec(spec_root: xml.Element, options: Options):
    types, enums, commands, feature, requirements = _parse_definitions(
        spec_root, options
    )
    prepared_enums = dict(prepare_enums(enums, options))
    prepared_commands = dict(prepare_commands(commands, prepared_enums, options))
    return _ParseResult(
        types=types,
        enums=prepared_enums,
        resource_wrappers=tuple(prepare_resource_wrappers(prepared_commands, options)),
        feature_levels=prepare_feature_levels(
            feature.api, requirements, prepared_commands
        ),
    )


def _check_preconditions(options: Options):
    if len(options.api) != len(options.version):
        raise SystemExit("ERROR: Must specify a version for every API")


def cli(*args) -> int:
    """Public CLI."""
    try:
        parsed_cli = make_argument_parser().parse_args(args)
    except SystemExit as exc:
        return exc.code

    options = Options(**(parsed_cli.__dict__))
    _check_preconditions(options)

    spec_root = xml.parse(options.spec_file).getroot()
    result = _parse_spec(spec_root, options)
    generate_code(
        options,
        result.types,
        result.enums.values(),
        result.feature_levels,
        result.resource_wrappers,
    )

    return 0


if __name__ == "__main__":
    sys.exit(cli(*sys.argv[1:]))
