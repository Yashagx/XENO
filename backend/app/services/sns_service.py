import json
import os
import logging
from app.services.aws_service import get_sns_client

logger = logging.getLogger(__name__)
SNS_TOPIC_ARN = os.getenv('AWS_SNS_TOPIC_ARN', '')


async def notify_campaign_ready(
    campaign_id: str, campaign_name: str, segment_size: int, predicted_revenue: float
) -> bool:
    """Publish campaign-ready notification to SNS topic."""
    sns = get_sns_client()
    if not sns or not SNS_TOPIC_ARN:
        return False
    try:
        message = {
            "event": "CAMPAIGN_READY",
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "segment_size": segment_size,
            "predicted_revenue": predicted_revenue,
            "action_required": "Login to Xeno Oracle to review and launch",
            "url": f"http://3.87.12.186:3000/campaigns/{campaign_id}"
        }
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Campaign Ready: {campaign_name}",
            Message=json.dumps(message, indent=2)
        )
        logger.info(f"SNS notification sent: CAMPAIGN_READY {campaign_id}")
        return True
    except Exception as e:
        logger.warning(f"SNS notify_campaign_ready failed: {e}")
        return False


async def notify_campaign_completed(campaign_id: str, campaign_name: str, actual_stats: dict) -> bool:
    """Publish campaign-completed notification to SNS topic."""
    sns = get_sns_client()
    if not sns or not SNS_TOPIC_ARN:
        return False
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Campaign Complete: {campaign_name} · ROI {actual_stats.get('roi', 0):.1f}x",
            Message=json.dumps({
                "event": "CAMPAIGN_COMPLETED",
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "stats": actual_stats
            }, indent=2)
        )
        logger.info(f"SNS notification sent: CAMPAIGN_COMPLETED {campaign_id}")
        return True
    except Exception as e:
        logger.warning(f"SNS notify_campaign_completed failed: {e}")
        return False
