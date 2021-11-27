"""Generator options."""

from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

import attr

from configargparse import ArgParser, YAMLConfigFileParser, ArgumentTypeError

from gladiator.mixins import CannotConvertToEnum, StringToEnumMixin
from gladiator.parse.feature import FeatureApi, FeatureVersion


class Case(StringToEnumMixin, Enum):
    """All supported code casings."""

    INITIAL = "initial"
    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"
    UPPER_CASE = "UPPER_CASE"


class Scope(StringToEnumMixin, Enum):
    """All supported wrapper scopes."""

    GLOBAL = "global"
    OBJECT = "object"


def _to_version(value: str):
    components = value.split(".")
    if len(components) != 2:
        raise ArgumentTypeError("must specify both major and minor components")

    try:
        major = int(components[0])
    except ValueError as exc:
        raise ArgumentTypeError("major component is not a number") from exc

    try:
        minor = int(components[1])
    except ValueError as exc:
        raise ArgumentTypeError("minor component is not a number") from exc

    return FeatureVersion(major=major, minor=minor)


def _enum(which: StringToEnumMixin):
    def wrapper(*args):
        try:
            return which.from_string(*args)
        except CannotConvertToEnum as exc:
            raise ArgumentTypeError(str(exc)) from exc

    return wrapper


@attr.s(auto_attribs=True, kw_only=True, slots=True, frozen=True)
class Options:
    # code style
    enum_case: Case
    function_case: Case
    enum_value_case: Case
    omit_prefix: bool

    # feature levels
    apis: Iterable[FeatureApi]
    versions: Iterable[FeatureVersion]
    intersect_features: bool

    # semantics
    scope: Scope
    enum_namespace: Optional[str]
    loader_or_class_namespace: Optional[str]
    loader_or_class_name_template: Optional[str]  #: {api} {major} {minor}

    # misc
    generate_resource_wrappers: bool
    resource_wrapper_namespace: Optional[str]
    template_overrides_dir: Optional[Path]
    output: Optional[Path]


def make_argument_parser():
    """Define the CLI."""
    cli = ArgParser(config_file_parser_class=YAMLConfigFileParser, add_help=True)
    cli.add_argument("--config-file", is_config_file=True)

    style = cli.add_argument_group("Style options")
    style.add_argument(
        "--enum-case",
        type=_enum(Case),
        default=Case.SNAKE_CASE,
        help=Case.options(),
    )
    style.add_argument(
        "--function-case",
        type=_enum(Case),
        default=Case.SNAKE_CASE,
        help=Case.options(),
    )
    style.add_argument(
        "--enum-value-case",
        type=_enum(Case),
        default=Case.SNAKE_CASE,
        help=Case.options(),
    )
    style.add_argument(
        "--omit-prefix",
        action="store_true",
        default=False,
        help="omit gl and GL_ prefixes",
    )

    levels = cli.add_argument_group("Feature level options")
    levels.add_argument(
        "--api",
        type=_enum(FeatureApi),
        required=True,
        nargs="+",
        help=FeatureApi.options(),
    )
    levels.add_argument(
        "--version",
        type=_to_version,
        required=True,
        nargs="+",
        help="versions for the given APIs (format: <major>.<minor>)",
    )
    levels.add_argument(
        "--intersect-features",
        action="store_true",
        default=False,
        help="collect least common denominator among the specified APIs",
    )

    sem = cli.add_argument_group("Semantic options")
    sem.add_argument(
        "--scope",
        type=_enum(Scope),
        default=Scope.GLOBAL,
        help=f"scope of OpenGL wrappers {Scope.options()}",
    )
    sem.add_argument("--enum-namespace", default=None, help="namespace enums reside in")
    sem.add_argument(
        "--loader-or-class-namespace",
        default=None,
        help="namespace the loaders or classes reside in",
    )
    sem.add_argument(
        "--loader-or-class-name-template",
        default=None,
        help="name template of loaders or classes (placeholders: {api}, {major}, {minor})",
    )

    misc = cli.add_argument_group("Miscellaneous options")
    misc.add_argument(
        "--generate-resource-wrappers",
        action="store_true",
        default=False,
        help="generate scoped resource wrappers",
    )
    misc.add_argument(
        "--resource-wrapper-namespace",
        default=None,
        help="namespace of resource wrappers",
    )
    misc.add_argument(
        "--template-overrides-dir",
        type=Path,
        default=None,
        help="dir containing files partially or fully overriding default templates",
    )
    misc.add_argument(
        "--output",
        type=Path,
        default=None,
        help="file to write code to (otherwise writes to stdout)",
    )

    return cli
