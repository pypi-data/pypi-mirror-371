from importlib import metadata
from pathlib import Path

if (Path(__file__).parent.parent.parent / "pyproject.toml").exists():
    # Set dynamically in .github/workflows/python-package-conda.yml
    # Fallback if not set
    v = "v2.2.4"
    __version__ = v.removeprefix("v")
else:
    __version__ = metadata.version("magtense")
