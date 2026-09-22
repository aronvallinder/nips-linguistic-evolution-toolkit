"""Investor-visible losses use the actual transfer, not the trustee's noised view (PR #30 review)."""
import math

from scripts.analyze_frontier_gap import apparent_loss, investor_visible_return_ratio


def test_denominators_disagree_on_a_loss():
    # Investor sent 4 (became 12); noise showed the trustee only 6. The trustee
    # returned 3 and the investor saw 3 come back: visible payoff 5 - 4 + 3 = 4.
    dyad = {"sent": 4, "received": 12, "received_communicated": 6, "returned": 3,
            "returned_communicated": 3, "investor_payoff_communicated": 4}
    trustee_view = dyad["returned_communicated"] / dyad["received_communicated"]
    assert trustee_view == 0.5  # the old denominator called this a fair round
    assert investor_visible_return_ratio(dyad) == 0.25
    assert apparent_loss(dyad)


def test_break_even_is_not_a_loss_and_zero_transfer_has_no_ratio():
    assert not apparent_loss({"investor_payoff_communicated": 5})
    assert math.isnan(investor_visible_return_ratio({"received": 0, "returned_communicated": 0}))
