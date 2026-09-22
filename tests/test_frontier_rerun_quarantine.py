"""Dry runs and --audit-only must never move run artifacts (PR #24 review, 2026-09-22)."""
import sys

import pytest

from scripts import run_frontier_rerun as launcher


@pytest.fixture
def invalid_final(tmp_path, monkeypatch):
    arm = next(iter(launcher.ARMS))
    shape = next(iter(launcher.EST_PER_RUN[arm]))
    final = tmp_path / "data/json/noise_experiments/run/final_rep00.json"
    final.parent.mkdir(parents=True)
    final.write_text('{"final": true}\n')
    sidecar = final.with_name("final_rep00.log")
    sidecar.write_text("log\n")
    job = {"path": final, "arm": arm, "shape": shape, "replicate": 0, "name": "run", "index": 0}
    monkeypatch.setattr(launcher, "ROOT", tmp_path)
    monkeypatch.setattr(launcher, "plan", lambda: [job])
    monkeypatch.setattr(launcher, "STAGES", {"smoke": lambda *_: True})

    def rejecting_audit(_job):
        raise RuntimeError(f"{final}: drifted settings")

    monkeypatch.setattr(launcher, "audit", rejecting_audit)
    return final, sidecar, tmp_path


def _snapshot(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("extra", [[], ["--audit-only"]])
def test_non_executing_modes_leave_invalid_finals_in_place(invalid_final, monkeypatch, extra):
    final, sidecar, root = invalid_final
    before = _snapshot(root)
    monkeypatch.setattr(sys, "argv", ["run_frontier_rerun.py", "--stage", "smoke", *extra])
    if extra:
        with pytest.raises((AssertionError, RuntimeError)):
            launcher.main()
    else:
        launcher.main()
    assert _snapshot(root) == before
    assert final.exists() and sidecar.exists()
    assert not (root / "data/json/noise_experiments" / launcher.OUTPUT / "quarantine").exists()
