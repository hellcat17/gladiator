"""Test command definition parsing."""

import xml.etree.ElementTree as xml

from gladiator.parser.command import parse_required_commands


def test_parse_enums(spec: xml.Element):
    for node in spec:
        if node.tag == "commands":
            commands = tuple(
                parse_required_commands(node, ["glAreTexturesResident", "glClear"])
            )
            resident = next(c for c in commands if c.name == "glAreTexturesResident")
            clear = next(c for c in commands if c.name == "glClear")

            assert resident.return_type.low_level == "GLboolean"
            assert resident.return_type.high_level == "Boolean"
            assert not resident.return_type.front_modifiers
            assert not resident.return_type.back_modifiers

            assert len(resident.params) == 3
            param_iter = iter(resident.params)

            size_param = next(param_iter)

            assert size_param.name == "n"
            assert size_param.type_.low_level == "GLsizei"
            assert size_param.type_.high_level == "GLsizei"

            texture_param = next(param_iter)
            assert texture_param.name == "textures"
            assert texture_param.type_.low_level == "GLuint"
            assert texture_param.type_.high_level == "Texture"
            assert texture_param.type_.front_modifiers == "const"
            assert texture_param.type_.back_modifiers == "*"

            residences_param = next(param_iter)
            assert residences_param.name == "residences"
            assert not residences_param.type_.front_modifiers
            assert residences_param.type_.back_modifiers == "*"

            assert clear.return_type.low_level == "void"
            assert clear.return_type.high_level == "void"
            assert not clear.return_type.front_modifiers
            assert not clear.return_type.back_modifiers

            assert len(clear.params) == 1
            param_iter = iter(clear.params)
            mask_param = next(param_iter)
            assert mask_param.name == "mask"
            assert mask_param.type_.low_level == "GLbitfield"
            assert mask_param.type_.high_level == "ClearBufferMask"
            assert not mask_param.type_.front_modifiers
            assert not mask_param.type_.back_modifiers
