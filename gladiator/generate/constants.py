"""Constants for shared use in templates."""

from enum import Enum

class Constants:
    type_namespace = "_t"
    detail_namespace = "_d"
    default_namespace = "gl"

class TemplateFiles(Enum):
    TYPES = "types.jinja2"
    ENUM_COLLECTION = "enum_collection.jinja2"
    ENUM = "enum.jinja2"
    LOADER = "loader.jinja2"

    @classmethod
    def overrides(cls):
        return f"{', '.join(e.value for e in cls)}"
