"""Initial package verification test."""

import devimage


def test_package_metadata():
    """Verify package name and version are defined."""
    assert devimage.__app_name__ == "DevImage"
    assert devimage.__version__ == "0.1.0"
