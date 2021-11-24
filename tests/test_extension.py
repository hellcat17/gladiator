"""Test extension definition parsing."""

import xml.etree.ElementTree as xml

from gladiator.parser.feature import FeatureApi
from gladiator.parser.extension import parse_required_extensions


def test_generate_extensions(spec: xml.Element):
    for node in spec:
        if node.tag == "extensions":
            extension = next(
                parse_required_extensions(
                    node, ["GL_AMD_framebuffer_multisample_advanced"]
                )
            )

            assert extension.name == "GL_AMD_framebuffer_multisample_advanced"
            assert "GL_RENDERBUFFER_STORAGE_SAMPLES_AMD" in extension.required_enums
            assert (
                "glRenderbufferStorageMultisampleAdvancedAMD"
                in extension.required_commands
            )

            assert len(extension.supported_apis) == 3
            api_iter = iter(extension.supported_apis)

            support_gl = next(api_iter)
            assert support_gl.api == FeatureApi.GL
            assert not support_gl.min_version
            assert support_gl.max_version.major == 3
            assert support_gl.max_version.minor == 0

            support_glcore = next(api_iter)
            assert support_glcore.api == FeatureApi.GL
            assert not support_glcore.max_version
            assert support_glcore.min_version.major == 3
            assert support_glcore.min_version.minor == 1

            support_gles2 = next(api_iter)
            assert support_gles2.api == FeatureApi.GLES2
            assert not support_gles2.max_version
            assert not support_gles2.min_version
