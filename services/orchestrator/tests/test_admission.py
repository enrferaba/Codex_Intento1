from orchestrator import admission


def test_allow_returns_bool():
    assert isinstance(admission.allow(), bool)
