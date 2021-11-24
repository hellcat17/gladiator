"""Optional value in functional fashion."""

from typing import Optional, Callable, TypeVar, Generic

T = TypeVar("T")
M = TypeVar("M")


class EmptyOptional(Exception):
    """Optional was empty when accessed."""


class OptionalValue(Generic[T]):  # pragma: no cover
    """Optional value."""

    def __init__(self, value: Optional[T]):
        self.value_ = value

    def map(self, function: Callable[[T], Optional[M]]) -> "OptionalValue[M]":
        """Map an optional value or return an empty optional value."""
        mapped = function(self.value_) if self.value_ is not None else None
        return OptionalValue(mapped if mapped is not None else None)

    def or_else(self, value: T) -> "OptionalValue[T]":
        """If the optional value is empty, return an alternative."""
        return self.__class__(value) if self.value_ is None else self

    @property
    def value(self) -> T:
        """Return the current value or raise an error if it is empty."""
        if self.value_ is None:
            raise EmptyOptional()
        return self.value_

    @property
    def value_or_none(self) -> Optional[T]:
        """Return the current value or None, if it is empty."""
        return self.value_

    @property
    def truthy_or_none(self) -> Optional[T]:
        """Return the value if it is 'truthy', None otherwise."""
        return self.value_ if self.value_ else None

    @property
    def has_value(self) -> bool:
        """Determine if this optional contains a value."""
        return self.value_ is not None
