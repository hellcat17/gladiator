"""Generator options."""

from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

import attr

from configargparse import ArgParser, YAMLConfigFileParser, ArgumentTypeError

from gladiator.generate.constants import TemplateFiles
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
    spec_file: Path = Path(__file__).parent.parent / "tests" / "resources" / "gl.xml"

    # code style
    enum_case: Case = Case.INITIAL
    function_case: Case = Case.INITIAL
    enum_value_case: Case = Case.INITIAL
    omit_prefix: bool = False

    # feature levels
    api: Sequence[FeatureApi] = ()
    version: Sequence[FeatureVersion] = ()

    # semantics
    scope: Scope = Scope.GLOBAL
    enum_namespace: Optional[str] = None
    loader_or_class_namespace: Optional[str] = None
    loader_or_class_name_template: Optional[str] = None  #: {api} {major} {minor}
    no_type_translation: bool = False

    # misc
    generate_resource_wrappers: bool = False
    resource_wrapper_namespace: Optional[str] = None
    template_overrides_dir: Optional[Path] = None
    output: Optional[Path] = None
    config_file: Optional[str] = None


def add_feature_level_options(cli: ArgParser):
    """Add feature level options to the given argument parser"""
    cli.add_argument(
        "--spec-file",
        required=True,
        help="OpenGL spec file path (https://github.com/KhronosGroup/OpenGL-Registry/blob/main/xml/gl.xml)",
    )
    cli.add_argument(
        "--api",
        type=_enum(FeatureApi),
        required=True,
        nargs="+",
        help=f"specifying multiple intersects the features {FeatureApi.options()}",
    )
    cli.add_argument(
        "--version",
        type=_to_version,
        required=True,
        nargs="+",
        help="versions for the given APIs (format: <major>.<minor>)",
    )


def make_argument_parser():
    """Define the CLI."""
    cli = ArgParser(
        config_file_parser_class=YAMLConfigFileParser,
        add_help=True,
        prog="python -m gladiator",
    )
    cli.add_argument("--config-file", is_config_file=True, default=None)

    style = cli.add_argument_group("Style options")
    style.add_argument(
        "--enum-case",
        type=_enum(Case),
        default=Case.INITIAL,
        help=Case.options(),
    )
    style.add_argument(
        "--function-case",
        type=_enum(Case),
        default=Case.INITIAL,
        help=Case.options(),
    )
    style.add_argument(
        "--enum-value-case",
        type=_enum(Case),
        default=Case.INITIAL,
        help=Case.options(),
    )
    style.add_argument(
        "--omit-prefix",
        action="store_true",
        default=False,
        help="omit gl and GL_ prefixes",
    )

    levels = cli.add_argument_group("Feature level options")
    add_feature_level_options(levels)

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
        help="name template of loaders or classes (placeholders if using single API: {api}, {major}, {minor})",
    )
    sem.add_argument(
        "--no-type-translation",
        action="store_true",
        default=False,
        help="do not translate OpenGL types (e.g. GLubyte) to cstdint defs (e.g. std::uint8_t)",
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
        help="namespace of resource wrappers (default: glw)",
    )
    misc.add_argument(
        "--template-overrides-dir",
        type=Path,
        default=None,
        help=f"dir containing files partially or fully overriding default templates (can contain: {TemplateFiles.overrides()})",
    )
    misc.add_argument(
        "--output",
        type=Path,
        default=None,
        help="file to write code to (otherwise writes to stdout)",
    )

    return cli
