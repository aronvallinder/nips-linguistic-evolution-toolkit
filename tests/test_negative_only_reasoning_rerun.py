from scripts.rerun_negative_only_crossmodel import EXPECTED_POLICIES, SET_NAMES, plan_rerun


def test_rerun_preserves_frozen_matrix_and_september8_profiles():
    planned = plan_rerun()
    assert len(SET_NAMES) == 18
    assert len(planned) == 270
    counts = {}
    for name, _index, combo, _path in planned:
        model = combo["model"]
        counts[model] = counts.get(model, 0) + 1
        assert combo["request_plan"].as_dict()["policy"] == EXPECTED_POLICIES[model]
        assert name.startswith("negative_only_reasoning_rerun_")
    assert counts == {model: 90 for model in EXPECTED_POLICIES}
