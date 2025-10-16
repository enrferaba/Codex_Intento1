from feriactl.utils import tabulate


def test_render_table():
    table = tabulate.render(["col"], [["value"]])
    assert "value" in table
