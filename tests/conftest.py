"""Global test configurations and pytest fixtures for DevImage."""

import os

import pytest

# Ensure all Qt tests run in headless offscreen mode
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qpa_offscreen():
    """Ensure offscreen platform is active."""
    return os.environ.get("QT_QPA_PLATFORM") == "offscreen"
