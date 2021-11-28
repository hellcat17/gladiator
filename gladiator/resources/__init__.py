from pathlib import Path

BASE_RESOURCE_PATH = Path(__file__).parent


def read_resource_file(file: str):
    """Read an entire resource file as utf-8."""
    return (BASE_RESOURCE_PATH / file).read_text(encoding="utf-8")
