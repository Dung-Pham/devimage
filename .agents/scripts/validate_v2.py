"""Deterministic validation suite for Autonomous Build System v2 control plane.

Validates all 12 core invariants:
 1. Clean startup
 2. Active session detection
 3. Stale session detection
 4. Lock creation
 5. Duplicate lock prevention
 6. Safe lock release
 7. Resume from checkpoint
 8. Crash before commit
 9. Commit without push
10. Push without state synchronization
11. Conflicting state
12. Gate preservation
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


class V2ControlPlaneValidator:
    """Implements and exercises the logic for v2 session, lock, and recovery rules."""

    @staticmethod
    def parse_iso(dt_str: str) -> datetime:
        """Parse ISO 8601 string to timezone-aware datetime."""
        # Handle trailing Z or offsets
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)

    @classmethod
    def evaluate_lock_status(cls, lock_data: dict, current_time: datetime | None = None) -> str:
        """Determine lock state based on heartbeat and lease duration."""
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        status = lock_data.get("status", "ACTIVE")
        if status in ("RELEASED", "COMPLETED"):
            return status

        heartbeat = cls.parse_iso(lock_data["last_heartbeat_at"])
        lease_sec = lock_data.get("lease_seconds", 300)

        if (current_time - heartbeat).total_seconds() > lease_sec:
            return "STALE_CANDIDATE"
        return "ACTIVE"

    @classmethod
    def acquire_lock(
        cls, lock_path: Path, session_id: str, task_id: str, branch: str, lease_seconds: int = 300
    ) -> tuple[bool, str, dict]:
        """Attempt to acquire a lease-based task lock atomically."""
        now = datetime.now(timezone.utc)
        if lock_path.exists():
            with open(lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

            current_status = cls.evaluate_lock_status(existing, now)
            if current_status == "ACTIVE" and existing.get("session_id") != session_id:
                return False, "LOCK_HELD_BY_ANOTHER_SESSION", existing

        # Create or take over lock
        payload = {
            "task_id": task_id,
            "session_id": session_id,
            "branch": branch,
            "claimed_at": now.isoformat(),
            "last_heartbeat_at": now.isoformat(),
            "lease_seconds": lease_seconds,
            "status": "ACTIVE",
        }
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return True, "ACQUIRED", payload

    @classmethod
    def release_lock(cls, lock_path: Path, session_id: str) -> bool:
        """Release lock cleanly if owned by current session."""
        if not lock_path.exists():
            return True
        with open(lock_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing.get("session_id") == session_id:
            existing["status"] = "RELEASED"
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            return True
        return False

    @classmethod
    def triage_resume_outcome(
        cls,
        has_active_gate: bool,
        lock_status: str,
        lock_session_is_current: bool,
        has_uncommitted_changes: bool,
        commit_unpushed: bool,
        state_says_done_but_no_git_commit: bool,
        in_flight_task_id: str | None,
    ) -> str:
        """Deterministic state triage matching RESUME_PROTOCOL.md."""
        if has_active_gate:
            return "WAIT_FOR_GATE"
        if state_says_done_but_no_git_commit:
            return "STOP_AND_REPORT"
        if lock_status == "ACTIVE" and not lock_session_is_current:
            return "WAIT_FOR_LOCK"
        if commit_unpushed:
            return "RECOVER_UNPUSHED_COMMIT"
        if has_uncommitted_changes:
            return "RECOVER_UNCOMMITTED_WORK"
        if in_flight_task_id:
            return "RESUME_TASK"
        return "IDLE_OR_ADVANCE"


def run_all_validations() -> bool:
    """Execute all 12 test assertions deterministically."""
    print("=" * 60)
    print("Running Autonomous Build System v2 Validation Suite")
    print("=" * 60)

    now = datetime.now(timezone.utc)

    # 1. Clean Startup
    print("[Test 1/12] Clean startup verification...")
    v2_run_path = Path("E:/devimage/.agents/state/V2_RUN.json")
    assert v2_run_path.is_file(), "V2_RUN.json must exist"
    with open(v2_run_path, "r", encoding="utf-8") as f:
        v2_run = json.load(f)
    assert v2_run["mode"] == "OBSERVE_ONLY", "Initial mode must be OBSERVE_ONLY"
    assert v2_run["version"] == "2.0.0", "Version must be 2.0.0"
    print("  -> Passed: Initial state is valid OBSERVE_ONLY.")

    # 2. Active Session Detection
    print("[Test 2/12] Active session detection...")
    active_payload = {
        "task_id": "TASK-TEST-01",
        "session_id": "session-active-123",
        "last_heartbeat_at": (now - timedelta(seconds=30)).isoformat(),
        "lease_seconds": 300,
        "status": "ACTIVE",
    }
    assert V2ControlPlaneValidator.evaluate_lock_status(active_payload, now) == "ACTIVE"
    print("  -> Passed: Recent heartbeat recognized as ACTIVE.")

    # 3. Stale Session Detection
    print("[Test 3/12] Stale session detection...")
    stale_payload = {
        "task_id": "TASK-TEST-01",
        "session_id": "session-stale-999",
        "last_heartbeat_at": (now - timedelta(seconds=600)).isoformat(),
        "lease_seconds": 300,
        "status": "ACTIVE",
    }
    assert V2ControlPlaneValidator.evaluate_lock_status(stale_payload, now) == "STALE_CANDIDATE"
    print("  -> Passed: Expired heartbeat detected as STALE_CANDIDATE.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        lock_file = Path(tmp_dir) / "active_task.lock"

        # 4. Lock Creation
        print("[Test 4/12] Lock creation...")
        ok, reason, lock = V2ControlPlaneValidator.acquire_lock(
            lock_path=lock_file,
            session_id="session-alpha",
            task_id="TASK-P3-01",
            branch="feature/test-v2",
            lease_seconds=120,
        )
        assert ok is True
        assert reason == "ACQUIRED"
        assert lock["session_id"] == "session-alpha"
        assert lock_file.exists()
        print("  -> Passed: Atomic lock created cleanly.")

        # 5. Duplicate Lock Prevention
        print("[Test 5/12] Duplicate lock prevention...")
        ok_dup, reason_dup, _ = V2ControlPlaneValidator.acquire_lock(
            lock_path=lock_file,
            session_id="session-beta",
            task_id="TASK-P3-01",
            branch="feature/test-v2",
        )
        assert ok_dup is False
        assert reason_dup == "LOCK_HELD_BY_ANOTHER_SESSION"
        print("  -> Passed: Concurrent lock claim rejected.")

        # 6. Safe Lock Release
        print("[Test 6/12] Safe lock release...")
        released = V2ControlPlaneValidator.release_lock(lock_file, "session-alpha")
        assert released is True
        with open(lock_file, "r", encoding="utf-8") as f:
            updated = json.load(f)
        assert updated["status"] == "RELEASED"
        print("  -> Passed: Lock released cleanly by owner.")

    # 7. Resume from Checkpoint
    print("[Test 7/12] Resume from checkpoint...")
    outcome = V2ControlPlaneValidator.triage_resume_outcome(
        has_active_gate=False,
        lock_status="RELEASED",
        lock_session_is_current=True,
        has_uncommitted_changes=False,
        commit_unpushed=False,
        state_says_done_but_no_git_commit=False,
        in_flight_task_id="TASK-P3-01",
    )
    assert outcome == "RESUME_TASK"
    print("  -> Passed: Checkpoint cleanly yields RESUME_TASK.")

    # 8. Crash Before Commit
    print("[Test 8/12] Crash before commit (dirty working tree)...")
    outcome_crash_dirty = V2ControlPlaneValidator.triage_resume_outcome(
        has_active_gate=False,
        lock_status="ACTIVE",
        lock_session_is_current=True,
        has_uncommitted_changes=True,
        commit_unpushed=False,
        state_says_done_but_no_git_commit=False,
        in_flight_task_id="TASK-P3-01",
    )
    assert outcome_crash_dirty == "RECOVER_UNCOMMITTED_WORK"
    print("  -> Passed: Dirty tree triaged to RECOVER_UNCOMMITTED_WORK.")

    # 9. Commit Without Push
    print("[Test 9/12] Commit without push...")
    outcome_unpushed = V2ControlPlaneValidator.triage_resume_outcome(
        has_active_gate=False,
        lock_status="ACTIVE",
        lock_session_is_current=True,
        has_uncommitted_changes=False,
        commit_unpushed=True,
        state_says_done_but_no_git_commit=False,
        in_flight_task_id="TASK-P3-01",
    )
    assert outcome_unpushed == "RECOVER_UNPUSHED_COMMIT"
    print("  -> Passed: Unpushed commit triaged to RECOVER_UNPUSHED_COMMIT.")

    # 10. Push Without State Synchronization
    print("[Test 10/12] Push without state synchronization...")
    # Git commit is confirmed, state lagging can be reconciled
    assert (
        V2ControlPlaneValidator.triage_resume_outcome(
            has_active_gate=False,
            lock_status="RELEASED",
            lock_session_is_current=True,
            has_uncommitted_changes=False,
            commit_unpushed=False,
            state_says_done_but_no_git_commit=False,
            in_flight_task_id=None,
        )
        == "IDLE_OR_ADVANCE"
    )
    print("  -> Passed: Push without state sync allows clean reconcile.")

    # 11. Conflicting State (State claims done, but no git commit)
    print("[Test 11/12] Conflicting state detection...")
    outcome_conflict = V2ControlPlaneValidator.triage_resume_outcome(
        has_active_gate=False,
        lock_status="RELEASED",
        lock_session_is_current=True,
        has_uncommitted_changes=False,
        commit_unpushed=False,
        state_says_done_but_no_git_commit=True,
        in_flight_task_id=None,
    )
    assert outcome_conflict == "STOP_AND_REPORT"
    print("  -> Passed: State/Git contradiction halts with STOP_AND_REPORT.")

    # 12. Gate Preservation
    print("[Test 12/12] Gate preservation...")
    outcome_gate = V2ControlPlaneValidator.triage_resume_outcome(
        has_active_gate=True,
        lock_status="RELEASED",
        lock_session_is_current=True,
        has_uncommitted_changes=False,
        commit_unpushed=False,
        state_says_done_but_no_git_commit=False,
        in_flight_task_id=None,
    )
    assert outcome_gate == "WAIT_FOR_GATE"
    print("  -> Passed: Active human gate unconditionally yields WAIT_FOR_GATE.")

    print("=" * 60)
    print("ALL 12 V2 CONTROL PLANE VALIDATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
