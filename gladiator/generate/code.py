"""Generate code using templates."""

from pathlib import Path
import re
from sys import stdout
from typing import Iterable, Optional
from gladiator.parse.type import TypeDefinition

from gladiator.options import Options
from gladiator.prepare.enum import PreparedEnum
from gladiator.prepare.feature import PreparedFeatureLevel
from gladiator.prepare.resource_wrapper import PreparedResourceWrapper
from gladiator.generate.constants import TemplateFiles
from gladiator.generate.templates import make_template_environment, render_template


class _Writer:
    def __init__(self, path: Optional[Path]):
        self.path = path
        self.file = stdout

    def __enter__(self):
        if self.path:
            self.file = open(str(self.path), "w", encoding="utf-8")
        return self

    def __exit__(self, _t, _v, _tb):
        if self.path:
            self.file.close()

    def write(self, text: str):
        self.file.write(text)


_REMOVE_REPEATING_NEWLINES_PATTERN = re.compile("\n+", re.MULTILINE)
_REMOVE_LEADING_WHITESPACE_PATTERN = re.compile("^[\t ]+", re.MULTILINE)


def _compress(code: str):
    return _REMOVE_REPEATING_NEWLINES_PATTERN.sub(
        "\n", _REMOVE_LEADING_WHITESPACE_PATTERN.sub("", code)
    )


def _generate_snippets(
    env,
    types: Iterable[TypeDefinition],
    enums: Iterable[PreparedEnum],
    levels: Iterable[PreparedFeatureLevel],
    resource_wrappers: Iterable[PreparedResourceWrapper],
):
    yield render_template(env, TemplateFiles.BEFORE.value)
    yield render_template(env, TemplateFiles.TYPES.value, types=types)
    yield render_template(env, TemplateFiles.ENUM_COLLECTION.value, enums=enums)
    yield render_template(env, TemplateFiles.LOADER.value, levels=levels)
    yield render_template(
        env, TemplateFiles.RESOURCE_WRAPPERS.value, resource_wrappers=resource_wrappers
    )
    yield render_template(env, TemplateFiles.AFTER.value)


def generate_code(
    options: Options,
    types: Iterable[TypeDefinition],
    enums: Iterable[PreparedEnum],
    levels: Iterable[PreparedFeatureLevel],
    resource_wrappers: Iterable[PreparedResourceWrapper],
):
    env = make_template_environment(options.template_overrides_dir, options, types)
    with _Writer(options.output) as output:
        code = "".join(_generate_snippets(env, types, enums, levels, resource_wrappers))
        output.write(_compress(code))
