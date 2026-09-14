"""Verify built archives include the import package, typing marker, and metadata."""

import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def main() -> None:
    """Inspect exactly one wheel and sdist in dist/."""
    wheels = list(Path("dist").glob("*.whl"))
    sdists = list(Path("dist").glob("*.tar.gz"))
    assert len(wheels) == len(sdists) == 1, "Expected exactly one wheel and one sdist"
    with zipfile.ZipFile(wheels[0]) as wheel:
        names = wheel.namelist()
        assert "chile_open_data_sdk/__init__.py" in names
        assert "chile_open_data_sdk/py.typed" in names
        for module in ("responses", "models", "constants", "types", "validation"):
            assert f"chile_open_data_sdk/{module}.py" in names
        assert not any("/_internal/" in name for name in names)
        assert not any(name.startswith("chile_open_data/") for name in names)
        metadata = BytesParser().parsebytes(
            wheel.read(next(n for n in names if n.endswith("/METADATA")))
        )
        assert metadata["Name"] == "chile-open-data-sdk"
        assert metadata["Version"] == "0.1.0"
        assert metadata["Requires-Python"] == ">=3.11"
        assert len(metadata.get_all("Requires-Dist", [])) == 2
        assert any(name.endswith("/LICENSE.md") for name in names)
    with tarfile.open(sdists[0]) as sdist:
        names = sdist.getnames()
        for suffix in (
            "/src/chile_open_data_sdk/py.typed",
            "/pyproject.toml",
            "/AGENTS.md",
            "/CLAUDE.md",
            "/README.md",
            "/LICENSE.md",
            "/docs/getting-started.md",
            "/tests/unit/test_core.py",
            "/examples/quickstart.py",
            "/uv.lock",
        ):
            assert any(name.endswith(suffix) for name in names), suffix
        assert not any("/src/chile_open_data/" in name for name in names)
        assert not any("/.cache/" in name or "/.venv/" in name for name in names)
    print("Wheel and sdist metadata, source contents, license, and py.typed verified.")


if __name__ == "__main__":
    main()
