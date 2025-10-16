from observability import anomaly


def test_ewma_returns_last_when_alpha_one():
    assert anomaly.ewma([1, 2, 3], alpha=1.0) == 3


def test_z_score_zero_without_history():
    assert anomaly.z_score(1.0, []) == 0.0
