import math

import numpy as np

from analyses._shared import (
    calculate_return_ratios,
    extract_game_metrics,
    infer_endowment,
)
from analyses.strategy_detection import extract_role_series, label_trustee
from analyses.trajectory_plotting import calculate_trajectory_metrics
from analyses.trajectory_plotting_rolling import rolling_average


def _round(round_number, sent, received, returned, investor_payoff, trustee_payoff):
    return {
        "round": round_number,
        "sent": sent,
        "received": received,
        "returned": returned,
        "investor_payoff": investor_payoff,
        "trustee_payoff": trustee_payoff,
        "balances": {"Agent_1": 0, "Agent_2": 0},
        "roles": {"Agent_1": "investor", "Agent_2": "trustee"},
    }


def test_infer_endowment_uses_full_payoff_identity():
    assert infer_endowment([4], [6], [7]) == 5


def test_zero_received_is_excluded_from_conditional_return_metrics():
    history = [
        _round(1, sent=4, received=12, returned=6, investor_payoff=7, trustee_payoff=6),
        _round(2, sent=0, received=0, returned=0, investor_payoff=5, trustee_payoff=0),
    ]

    ratios = calculate_return_ratios([6, 0], [12, 0])
    assert ratios[0] == 0.5
    assert math.isnan(ratios[1])

    shared_metrics = extract_game_metrics({"conversation_history": history})
    assert shared_metrics["mean_trust_ratio"] == 0.4
    assert shared_metrics["mean_return_ratio"] == 0.5
    assert shared_metrics["std_return_ratio"] == 0.0

    trajectory_metrics = calculate_trajectory_metrics(history)
    assert trajectory_metrics["trust_score"] == 0.4
    assert trajectory_metrics["cooperation_score"] == 0.5


def test_all_zero_receipts_produce_undefined_return_summary():
    history = [
        _round(1, sent=0, received=0, returned=0, investor_payoff=5, trustee_payoff=0)
    ]
    metrics = extract_game_metrics({"conversation_history": history})
    assert math.isnan(metrics["mean_return_ratio"])
    assert math.isnan(metrics["std_return_ratio"])


def test_no_return_opportunity_is_not_labelled_as_defection():
    history = [
        _round(1, sent=0, received=0, returned=0, investor_payoff=5, trustee_payoff=0)
    ]
    series = extract_role_series({"conversation_history": history})
    assert series["Agent_2"]["trustee_return_rates"] == []
    assert label_trustee(series["Agent_2"]["trustee_return_rates"]) == "unknown"


def test_return_ratio_shapes_must_match():
    with np.testing.assert_raises(ValueError):
        calculate_return_ratios([1], [2, 3])


def test_rolling_average_ignores_undefined_return_rounds():
    smoothed = rolling_average([1.0, np.nan, 3.0, 4.0, 5.0], window=3)
    np.testing.assert_allclose(smoothed, [1.0, 2.0, 3.5, 4.0, 4.5])
