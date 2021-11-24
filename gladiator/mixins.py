"""Common mixin classes."""


class CannotConvertToEnum(ValueError):
    """Cannot convert from string to enum."""

    def __init__(self, cls, value):
        super().__init__(
            f"Cannot convert '{value}' to enum '{cls.__name__}'; needs to be one of {cls.options()}"
        )


class StringToEnumMixin:
    """Convert a string to an enum."""

    @classmethod
    def options(cls):
        return f"({'|'.join(e.value for e in cls)})"

    @classmethod
    def from_string(cls, value: str):
        try:
            return next(a for a in cls if a.value == value)  # type: ignore
        except StopIteration as exc:
            raise CannotConvertToEnum(cls, value) from exc
