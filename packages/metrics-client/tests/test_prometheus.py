from metrics_client import prometheus


def test_client_has_query_method():
    client = prometheus.PrometheusClient.__new__(prometheus.PrometheusClient)
    assert hasattr(client, "query")
