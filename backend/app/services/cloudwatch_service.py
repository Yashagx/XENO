import os
import logging
from datetime import datetime
from app.services.aws_service import get_cloudwatch_client

logger = logging.getLogger(__name__)
NAMESPACE = "XenoOracle"


async def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: dict = None):
    """Push a single metric to CloudWatch. Fire-and-forget."""
    cw = get_cloudwatch_client()
    if not cw:
        return
    try:
        dim_list = [{"Name": k, "Value": v} for k, v in (dimensions or {}).items()]
        if not dim_list:
            dim_list = [{"Name": "Environment", "Value": os.getenv("ENVIRONMENT", "development")}]
        cw.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': dim_list
            }]
        )
    except Exception as e:
        logger.debug(f"CloudWatch metric failed (non-critical): {e}")


async def metric_campaign_created(): await put_metric("CampaignsCreated", 1)
async def metric_campaign_completed(roi: float): await put_metric("CampaignROI", roi, "None")
async def metric_messages_sent(count: int): await put_metric("MessagesSent", float(count))
async def metric_agent_error(agent_name: str): await put_metric("AgentErrors", 1, dimensions={"Agent": agent_name})
async def metric_api_latency(endpoint: str, ms: float): await put_metric("APILatency", ms, "Milliseconds", {"Endpoint": endpoint[:50]})
