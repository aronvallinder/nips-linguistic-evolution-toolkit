"""Shared helpers used across analysis scripts.

Keep this module minimal — only helpers duplicated in 2+ places belong here.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.experiment_condition import check_conditions, comparison_condition, read_final_run


def configure_matplotlib() -> None:
    """Set the non-interactive Agg backend.

    Must be called before any `import matplotlib.pyplot`. Safe to call more
    than once.
    """
    import matplotlib
    matplotlib.use("Agg")


def load_simulation_data(filepath: str) -> Dict:
    """Load a simulation state JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_simulation_runs(filepaths, *, allowed_differences=None, legacy_reason=None):
    """Read completed runs and require explicit differences before pooling them."""
    paths = [str(Path(path).resolve()) for path in filepaths]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate run paths cannot count as independent inputs")
    runs = {path: read_final_run(path) for path in paths}
    hashes = [hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths]
    if len(hashes) != len(set(hashes)):
        raise ValueError("Duplicate run contents cannot count as independent inputs")
    check_conditions([comparison_condition(data, legacy_reason) for data in runs.values()], allowed_differences)
    return runs


def write_output_provenance(output_dir, filepaths, *, allowed_differences=None, legacy_reason=None):
    from src.experiment_condition import output_provenance

    directory = Path(output_dir)
    outputs = [path for path in directory.rglob("*") if path.is_file() and path != directory / "provenance.json"]
    document = output_provenance(filepaths, outputs, allowed_differences, legacy_reason, output_root=directory)
    (directory / "provenance.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def infer_endowment(
    sent: Sequence[float],
    returned: Sequence[float],
    investor_payoff: Sequence[float],
) -> float:
    """Recover the sender's fixed endowment from recorded game outcomes.

    The game payoff is ``endowment - sent + returned``, so the endowment is
    ``investor_payoff + sent - returned``.  Use the median valid round to be
    robust to small inconsistencies in legacy result files.
    """
    sent_values = np.asarray(sent, dtype=float)
    returned_values = np.asarray(returned, dtype=float)
    payoff_values = np.asarray(investor_payoff, dtype=float)
    if not (
        sent_values.shape == returned_values.shape == payoff_values.shape
    ):
        raise ValueError("sent, returned, and investor_payoff must have matching shapes")

    candidates = payoff_values + sent_values - returned_values
    valid = candidates[np.isfinite(candidates) & (candidates > 0)]
    if valid.size == 0:
        raise ValueError("Could not infer a positive endowment from game outcomes")
    return float(np.median(valid))


def calculate_return_ratios(
    returned: Sequence[float], received: Sequence[float]
) -> np.ndarray:
    """Return ``returned / received``, leaving no-opportunity rounds undefined.

    A receiver who gets zero cannot choose a positive return, so that round
    contains no observation of trustee generosity.  It is represented as NaN
    and should be excluded from conditional return summaries.
    """
    returned_values = np.asarray(returned, dtype=float)
    received_values = np.asarray(received, dtype=float)
    if returned_values.shape != received_values.shape:
        raise ValueError("returned and received must have matching shapes")

    ratios = np.full(received_values.shape, np.nan, dtype=float)
    np.divide(
        returned_values,
        received_values,
        out=ratios,
        where=received_values > 0,
    )
    return ratios


def extract_game_metrics(data: Dict, endowment: Optional[float] = None) -> Optional[Dict]:
    """Extract cooperation metrics from a simulation JSON file.

    Args:
        data: parsed simulation JSON (the dict returned by `load_simulation_data`).
        endowment: initial per-round endowment. If None, it is derived from the
            payoff identity ``investor_payoff + sent - returned``.

    Returns:
        Metrics dict, or None if the simulation has no valid game rounds.
    """
    history = data.get("conversation_history", [])

    game_rounds = [
        r for r in history
        if r.get("sent") is not None and r.get("returned") is not None
    ]

    if not game_rounds:
        return None

    sent = np.array([r["sent"] for r in game_rounds])
    received = np.array([r["received"] for r in game_rounds])
    returned = np.array([r["returned"] for r in game_rounds])
    investor_payoff = np.array([r["investor_payoff"] for r in game_rounds])
    trustee_payoff = np.array([r["trustee_payoff"] for r in game_rounds])

    agent_1_balances = []
    agent_2_balances = []
    for r in game_rounds:
        balances = r.get("balances", {})
        agent_1_balances.append(balances.get("Agent_1", 0))
        agent_2_balances.append(balances.get("Agent_2", 0))

    if endowment is None:
        endowment = infer_endowment(sent, returned, investor_payoff)

    trust_ratios = sent / endowment if endowment > 0 else sent * 0
    return_ratios = calculate_return_ratios(returned, received)
    observed_return_ratios = return_ratios[np.isfinite(return_ratios)]
    mean_return_ratio = (
        float(np.mean(observed_return_ratios))
        if observed_return_ratios.size
        else float("nan")
    )
    std_return_ratio = (
        float(np.std(observed_return_ratios))
        if observed_return_ratios.size
        else float("nan")
    )

    return {
        "num_rounds": len(game_rounds),
        "mean_sent": float(np.mean(sent)),
        "std_sent": float(np.std(sent)),
        "mean_returned": float(np.mean(returned)),
        "std_returned": float(np.std(returned)),
        "mean_trust_ratio": float(np.mean(trust_ratios)),
        "std_trust_ratio": float(np.std(trust_ratios)),
        "mean_return_ratio": mean_return_ratio,
        "std_return_ratio": std_return_ratio,
        "mean_investor_payoff": float(np.mean(investor_payoff)),
        "mean_trustee_payoff": float(np.mean(trustee_payoff)),
        "final_investor_payoff": float(investor_payoff[-1]),
        "final_trustee_payoff": float(trustee_payoff[-1]),
        "cooperation_stability": std_return_ratio,
        "agent_1_balances": agent_1_balances,
        "agent_2_balances": agent_2_balances,
    }
