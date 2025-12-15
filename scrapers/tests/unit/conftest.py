"""Pytest configuration for unit tests."""

import pytest

# Check if scrapling is available - if not, skip all comando tests
try:
    import scrapling  # noqa: F401

    HAS_SCRAPLING = True
except (ImportError, FileNotFoundError):
    HAS_SCRAPLING = False


@pytest.fixture(scope="session", autouse=True)
def check_scrapling_availability():
    """Auto-skip all comando tests if scrapling not available."""
    if not HAS_SCRAPLING:
        pytest.skip(
            "scrapling and camoufox are optional dependencies. Install with: uv add scrapling camoufox",
            allow_module_level=True,
        )
