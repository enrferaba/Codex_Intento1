from agent import policies


def test_allowed_command():
    assert policies.is_allowed("pytest -q")


def test_denied_command():
    assert not policies.is_allowed("rm -rf /")
