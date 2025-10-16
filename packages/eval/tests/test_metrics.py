from eval import metrics_ndcg, metrics_ece, precision_coverage, ab_test


def test_ndcg_order_invariant():
    scores = [1.0, 0.5, 0.0]
    assert metrics_ndcg.ndcg(scores) <= 1.0


def test_ece_zero_for_perfect_calibration():
    bins = [(1.0, 0.8, 0.8)]
    assert metrics_ece.ece(bins) == 0.0


def test_precision_coverage_no_selection():
    precision, coverage = precision_coverage.precision_at_threshold([0.1, 0.2], [True, False], 0.9)
    assert coverage == 0.0
    assert precision == 1.0


def test_ab_winner():
    control = ab_test.VariantResult("control", ndcg=0.6, p95=1.2, ece=0.05, cost=1.0)
    candidate = ab_test.VariantResult("candidate", ndcg=0.61, p95=1.1, ece=0.04, cost=0.9)
    assert ab_test.is_winner(candidate, control)
