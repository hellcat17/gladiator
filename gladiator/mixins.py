"""Common mixin classes."""


class CannotConvertToEnum(Exception):
    """Cannot convert from string to enum."""

    def __init__(self, cls, value):
        super().__init__("Cannot convert '{}' to enum '{}'".format(value, cls.__name__))


class StringToEnumMixin:
    """Convert a string to an enum."""

    @classmethod
    def from_string(cls, value: str):
        try:
            return next(a for a in cls if a.value == value)  # type: ignore
        except StopIteration:
            raise CannotConvertToEnum(cls, value)
