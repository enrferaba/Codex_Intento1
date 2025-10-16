from model_gateway import router


def test_route_small():
    assert router.route(1.0) == "small"
