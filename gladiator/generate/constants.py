"""Constants for shared use in templates."""

from enum import Enum
from pathlib import Path


_ENUM_UT_OVERRIDES = [
    ov.split(",")
    for ov in (
        (
            Path(__file__).parent.parent.parent
            / "data"
            / "enum_underlying_type_overrides"
        )
        .read_text(encoding="utf-8")
        .split("\n")
    )
    if ov
]


class Constants:
    type_namespace = "_t"
    detail_namespace = "_d"
    default_namespace = "gl"
    enum_underlying_type_overrides = dict(_ENUM_UT_OVERRIDES)


class TemplateFiles(Enum):
    TYPES = "types.jinja2"
    ENUM_COLLECTION = "enum_collection.jinja2"
    ENUM = "enum.jinja2"
    LOADER = "loader.jinja2"

    @classmethod
    def overrides(cls):
        return f"{', '.join(e.value for e in cls)}"
