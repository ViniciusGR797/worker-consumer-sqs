import pytest
from unittest.mock import patch, MagicMock

with patch("utils.metrics.boto3.client") as mock_client:
    from utils.metrics import put_metric

def test_put_metric_success_default_namespace():
    mock_cw = MagicMock()
    # o patch do boto3.client vai retornar mock_cw
    put_metric.__globals__["cloudwatch"] = mock_cw

    put_metric("TestMetric", 5)

    mock_cw.put_metric_data.assert_called_once_with(
        Namespace="Worker-consumer-SQS/Messages",
        MetricData=[{
            "MetricName": "TestMetric",
            "Value": 5,
            "Unit": "Count"
        }]
    )

def test_put_metric_success_custom_namespace():
    mock_cw = MagicMock()
    put_metric.__globals__["cloudwatch"] = mock_cw

    put_metric("CustomMetric", 10, namespace="Custom/Namespace")

    mock_cw.put_metric_data.assert_called_once_with(
        Namespace="Custom/Namespace",
        MetricData=[{
            "MetricName": "CustomMetric",
            "Value": 10,
            "Unit": "Count"
        }]
    )

def test_put_metric_raises():
    mock_cw = MagicMock()
    mock_cw.put_metric_data.side_effect = Exception("Fail metric")
    put_metric.__globals__["cloudwatch"] = mock_cw

    import pytest
    with pytest.raises(Exception):
        put_metric("FailMetric", 1)
