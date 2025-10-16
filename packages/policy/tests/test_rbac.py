from policy import rbac


def test_admin_can_eval():
    assert rbac.can("admin", "eval")


def test_user_cannot_admin():
    assert not rbac.can("user", "admin")
