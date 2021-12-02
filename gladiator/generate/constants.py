"""Constants for shared use in templates."""

from enum import Enum

from gladiator.resources import read_resource_file


_ENUM_UT_OVERRIDES = [
    ov.split(",")
    for ov in read_resource_file("data/enum_underlying_type_overrides").split("\n")
    if ov
]


class Constants:
    type_namespace = "_t"
    detail_namespace = "_d"
    default_namespace = "gl"
    default_resource_wrapper_namespace = "glw"
    enum_underlying_type_overrides = dict(_ENUM_UT_OVERRIDES)


class TemplateFiles(Enum):
    TYPES = "types.jinja2"
    ENUM_COLLECTION = "enum_collection.jinja2"
    ENUM = "enum.jinja2"
    LOADER = "loader.jinja2"
    RESOURCE_WRAPPERS = "resource_wrappers.jinja2"
    BEFORE = "before.jinja2"
    AFTER = "after.jinja2"

    @classmethod
    def overrides(cls):
        return f"{', '.join(e.value for e in cls)}"
