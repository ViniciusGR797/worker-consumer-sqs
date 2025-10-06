import boto3
from utils.config import Config

cloudwatch = boto3.client("cloudwatch", region_name=Config.REGION)


def put_metric(name, value, namespace="Worker-consumer-SQS/Messages"):
    cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[{
            "MetricName": name,
            "Value": value,
            "Unit": "Count"
        }]
    )
