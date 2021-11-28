"""Template preparation and rendering."""

from pathlib import Path
from typing import Optional, TYPE_CHECKING

import jinja2

from gladiator.generate.constants import Constants, TemplateFiles
from gladiator.prepare.command import CommandType, ConversionType
from gladiator.options import Scope

if TYPE_CHECKING:
    from gladiator.options import Options


BASE_TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


def _make_globals(options: "Options"):
    return {
        "options": options,
        "constants": Constants,
        "templates": TemplateFiles,
        "Scope": Scope,
        "CommandType": CommandType,
        "ConversionType": ConversionType,
    }


def make_template_environment(overrides: Optional[Path], options: "Options"):
    """Make a Jinja2 environment with a file system loader respecting possible
    template overrides and predefined globals.
    """
    includes = [BASE_TEMPLATE_DIR] + ([overrides] if overrides else [])
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(includes, followlinks=True), autoescape=True
    )
    env.globals.update(_make_globals(options))
    return env


def render_template(env: jinja2.Environment, template: str, **context):
    """Render the given template with an additional context being made available in it."""
    return env.get_template(template).render(**context)
