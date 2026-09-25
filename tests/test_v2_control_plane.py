"""PyTest integration for Autonomous Build System v2 control plane validation."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path if needed
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / ".agents" / "scripts"))

from validate_v2 import run_all_validations  # noqa: E402


def test_v2_control_plane_all_scenarios() -> None:
    """Verify all 12 deterministic control plane scenarios pass."""
    assert run_all_validations() is True


def test_v2_schema_and_files_exist() -> None:
    """Verify that all required v2 specification files are present."""
    required_files = [
        ROOT_DIR / ".agents/controller/BUILD_CONTROLLER_V2.md",
        ROOT_DIR / ".agents/controller/migration.md",
        ROOT_DIR / ".agents/workers/session-bootstrap.md",
        ROOT_DIR / ".agents/handoff/SESSION_HANDOFF.md",
        ROOT_DIR / ".agents/handoff/RESUME_PROTOCOL.md",
        ROOT_DIR / ".agents/handoff/SESSION_REGISTRY.md",
        ROOT_DIR / ".agents/handoff/handoff-template.md",
        ROOT_DIR / ".agents/locks/LOCK_PROTOCOL.md",
        ROOT_DIR / ".agents/recovery/CRASH_RECOVERY.md",
        ROOT_DIR / ".agents/recovery/stale-session-policy.md",
        ROOT_DIR / ".agents/rules/v2-safety-rules.md",
        ROOT_DIR / ".agents/state/V2_RUN.json",
        ROOT_DIR / ".agents/state/SESSION.json",
        ROOT_DIR / ".agents/state/SESSION_REGISTRY.md",
        ROOT_DIR / ".agents/tasks/templates/task-template-v2.md",
    ]
    for path in required_files:
        assert path.is_file(), f"Required v2 control plane file missing: {path}"
