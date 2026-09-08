"""Offline checks for the archived reports' reproduction commands."""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_format_report_uses_each_runs_endowment(tmp_path):
    directories = [
        "data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/claude-sonnet-4.5/myth_game/noisy8_crossmodel_negative_defectors25_twotask_r3",
        "data/json/noise_experiments/fmt_confound_20260904/fmt_claude_defectors25_myth_game_json_only_n5",
        "data/json/noise_experiments/fmt_confound_20260904/fmt_claude_defectors25_myth_game_reasoning_then_json_n5",
    ]
    for directory, endowment in zip(directories, (10, 20, 8)):
        folder = tmp_path / directory
        folder.mkdir(parents=True)
        data = {
            "run_metadata": {}, "task_order": ["myth", "game"],
            "agents": {"Agent_1": {"interaction_history": [
                {"prompt": "initial myth", "metadata": {"task": "myth", "round": 1}},
                {"prompt": "later myth", "metadata": {"task": "myth", "round": 2}},
                {"response": {"content": '{"send": 4}'}, "metadata": {"task": "game"}},
            ]}},
            "game_data": {"balances": {"Agent_1": 20}},
            "conversation_history": [{"dyads": [{
                "investor": "Agent_1", "trustee": "Agent_1", "sent": 4,
                "received": 12, "returned": 3, "investor_payoff": endowment - 1,
            }]}],
        }
        for repeat in range(2):
            (folder / f"run{repeat}.json").write_text(json.dumps(data))
    output = tmp_path / "summary.json"
    subprocess.run([
        sys.executable, str(ROOT / "reports/api_audit_reassessment_2026_09_08/summarize_format.py"),
        "--repo-root", str(tmp_path), "--output", str(output),
    ], check=True, capture_output=True, text=True)
    rows = json.loads(output.read_text())
    assert [row["send_fraction"] for row in rows] == [0.4, 0.4, 0.2, 0.2, 0.5, 0.5]


def test_pilot_help_works_outside_repository(tmp_path):
    # --help exits before reading the archive or making any paid request.
    result = subprocess.run([
        sys.executable, str(ROOT / "reports/reasoning_cost_pilot_2026_09_08/run_pilot.py"), "--help",
    ], cwd=tmp_path, check=True, capture_output=True, text=True)
    assert "usage:" in result.stdout
