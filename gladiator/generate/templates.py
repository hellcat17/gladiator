"""Template preparation and rendering."""

from pathlib import Path
from typing import Iterable, Optional, TYPE_CHECKING

import jinja2

from gladiator.generate.constants import Constants, TemplateFiles
from gladiator.parse.feature import FeatureApi, FeatureVersion
from gladiator.parse.type import TypeDefinition
from gladiator.prepare.command import CommandType, ConversionType
from gladiator.prepare.resource_wrapper import ResourceWrapperType
from gladiator.options import Scope
from gladiator.resources import BASE_RESOURCE_PATH

if TYPE_CHECKING:
    from gladiator.options import Options


BASE_TEMPLATE_DIR = BASE_RESOURCE_PATH / "templates"


def _make_api_version_identifier(
    apis: Iterable[FeatureApi], versions: Iterable[FeatureVersion]
):
    for api, version in zip(apis, versions):
        yield f"{api.value.upper()}_{version.major}_{version.minor}"


def _make_globals(options: "Options", types: Iterable[TypeDefinition]):
    return {
        "options": options,
        "constants": Constants,
        "templates": TemplateFiles,
        "opengl_types": [t.name for t in types],
        "Scope": Scope,
        "CommandType": CommandType,
        "ConversionType": ConversionType,
        "ResourceWrapperType": ResourceWrapperType,
        "api_version_id": "__".join(
            _make_api_version_identifier(options.api, options.version)
        ),
    }


def make_template_environment(
    overrides: Optional[Path], options: "Options", types: Iterable[TypeDefinition]
):
    """Make a Jinja2 environment with a file system loader respecting possible
    template overrides and predefined globals.
    """
    includes = [BASE_TEMPLATE_DIR] + ([overrides] if overrides else [])
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(includes, followlinks=True), autoescape=True
    )
    env.globals.update(_make_globals(options, types))
    return env


def render_template(env: jinja2.Environment, template: str, **context):
    """Render the given template with an additional context being made available in it."""
    return env.get_template(template).render(**context)
