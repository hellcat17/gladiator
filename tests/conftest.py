"""Configure the test environment."""

from pathlib import Path
import xml.etree.ElementTree as xml

import pytest


TEST_ROOT = Path(__file__).parent


@pytest.fixture(scope="session")
def spec() -> xml.Element:
    return xml.parse(TEST_ROOT / "resources" / "gl.xml").getroot()


@pytest.fixture(scope="session")
def resource_path() -> Path:
    return TEST_ROOT / "resources"
