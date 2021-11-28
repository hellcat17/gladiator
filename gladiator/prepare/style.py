"""Transform function and enum names according to the preferred style options."""

from typing import Sequence

from gladiator.options import Case
from gladiator.resources import read_resource_file


_RESERVED_KEYWORDS = [
    t for t in read_resource_file("data/cpp_keywords").split("\n") if t
]


def _get_word_boundaries(symbol: str):
    b_start = 0
    was_lower = False

    for index, char in enumerate(symbol):
        if was_lower and char.isupper():
            yield b_start, index
            b_start = index
        elif char == "_":
            yield b_start, index
            b_start = index + 1
        was_lower = char.islower()

    yield b_start, len(symbol)


def _split_into_words(symbol: str):
    for start, end in _get_word_boundaries(symbol):
        yield symbol[start:end]


def _omit_gl_str(symbol: str):
    if symbol.startswith("gl"):
        return symbol[2:]
    if symbol.startswith("GL_"):
        return symbol[3:]
    return symbol


def _omit_gl(words: Sequence[str], omit_gl: bool):
    return words[1:] if omit_gl and words[0].lower().startswith("gl") else words


def _camel_case(words: Sequence[str]):
    yield words[0].lower()

    for word in words[1:]:
        yield word.capitalize()


def _apply_case(words: Sequence[str], case: Case):
    if case == Case.SNAKE_CASE:
        return "_".join(w.lower() for w in words)
    if case == Case.UPPER_CASE:
        return "_".join(w.upper() for w in words)
    if case == Case.PASCAL_CASE:
        return "".join(w.capitalize() for w in words)
    if case == Case.CAMEL_CASE:
        return "".join(_camel_case(words))
    return "".join(words)


def _resolve_conflicts(symbol: str):
    while symbol in _RESERVED_KEYWORDS:
        symbol = f"{symbol}_"
    return symbol


def transform_symbol(symbol: str, case: Case, omit_gl: bool):
    """Transform the given symbol according to the provided style options."""
    if not symbol:
        raise ValueError("Must provide non-empty string")

    if case == Case.INITIAL:
        return _omit_gl_str(symbol) if omit_gl else symbol

    return _resolve_conflicts(
        _apply_case(_omit_gl(tuple(_split_into_words(symbol)), omit_gl), case)
    )
