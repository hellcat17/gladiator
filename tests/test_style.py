"""Test symbol transformation with style options."""

import pytest

from gladiator.options import Case
from gladiator.prepare.style import transform_symbol


_TEST_CASES = (
    "glCompressedTexImage2D",
    "GL_POSITION",
    "glPixelStoref",
    "glPixelStorei",
    "glGetTexParameterfv",
    "glColor3d",
    "glColor3usv",
    "glColorMaterial",
    "GL_ALPHA8",
    "GL_PROXY_TEXTURE_2D",
    "TextureLevel",
    "GL_RGBA32F",
    "glTexParameterIiv",
    "GL_RG8_EXT",
    "GL_R32UI",
)

_OMIT_GL_NO_TRANSFORM = (
    "CompressedTexImage2D",
    "POSITION",
    "PixelStoref",
    "PixelStorei",
    "GetTexParameterfv",
    "Color3d",
    "Color3usv",
    "ColorMaterial",
    "ALPHA8",
    "PROXY_TEXTURE_2D",
    "TextureLevel",
    "RGBA32F",
    "TexParameterIiv",
    "RG8_EXT",
    "R32UI",
)

_SNAKE_CASE = (
    "compressed_tex_image2d",
    "position",
    "pixel_storef",
    "pixel_storei",
    "get_tex_parameterfv",
    "color3d",
    "color3usv",
    "color_material",
    "alpha8",
    "proxy_texture_2d",
    "texture_level",
    "rgba32f",
    "tex_parameter_iiv",
    "rg8_ext",
    "r32ui",
)

_UPPER_CASE = tuple(w.upper() for w in _SNAKE_CASE)

_CAMEL_CASE = (
    "compressedTexImage2d",
    "position",
    "pixelStoref",
    "pixelStorei",
    "getTexParameterfv",
    "color3d",
    "color3usv",
    "colorMaterial",
    "alpha8",
    "proxyTexture2d",
    "textureLevel",
    "rgba32f",
    "texParameterIiv",
    "rg8Ext",
    "r32ui",
)

_PASCAL_CASE = tuple(w[0].upper() + w[1:] for w in _CAMEL_CASE)


@pytest.mark.parametrize("input_", _TEST_CASES)
def test_no_transform(input_: str):
    """Assert that no transformation yields the same results."""
    assert transform_symbol(input_, Case.INITIAL, False) == input_


@pytest.mark.parametrize("input_,output", zip(_TEST_CASES, _OMIT_GL_NO_TRANSFORM))
def test_omit_gl_no_transform(input_: str, output: str):
    """Assert that only the gl or GL_ prefix is stripped."""
    assert transform_symbol(input_, Case.INITIAL, True) == output


@pytest.mark.parametrize("input_,output", zip(_TEST_CASES, _SNAKE_CASE))
def test_snake_case(input_: str, output: str):
    """Assert that the OpenGL command or enum is converted to snake case."""
    assert transform_symbol(input_, Case.SNAKE_CASE, True) == output


@pytest.mark.parametrize("input_,output", zip(_TEST_CASES, _UPPER_CASE))
def test_upper_case(input_: str, output: str):
    """Assert that the OpenGL command or enum is converted to upper case."""
    assert transform_symbol(input_, Case.UPPER_CASE, True) == output


@pytest.mark.parametrize("input_,output", zip(_TEST_CASES, _CAMEL_CASE))
def test_camel_case(input_: str, output: str):
    """Assert that the OpenGL command or enum is converted to camel case."""
    assert transform_symbol(input_, Case.CAMEL_CASE, True) == output


@pytest.mark.parametrize("input_,output", zip(_TEST_CASES, _PASCAL_CASE))
def test_pascal_case(input_: str, output: str):
    """Assert that the OpenGL command or enum is converted to pascal case."""
    assert transform_symbol(input_, Case.PASCAL_CASE, True) == output
