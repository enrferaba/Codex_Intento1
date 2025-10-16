from sdk import schemas


def test_query_request_model():
    model = schemas.QueryRequest(query="hola")
    assert model.query == "hola"
