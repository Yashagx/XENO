import os
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user, require_role
from app.models.auth import User
from app.services.aws_service import get_s3_client, get_ses_client, get_sns_client, get_cloudwatch_client, get_secrets_client
from app.services.s3_service import get_s3_storage_stats

router = APIRouter()


@router.get("/status")
async def aws_status(current_user: User = Depends(require_role("admin"))):
    """Return AWS service connection status. Available to admin only."""
    # S3
    s3_stats = await get_s3_storage_stats()
    s3_info = {
        "connected": s3_stats.get("connected", False),
        "bucket": s3_stats.get("bucket", os.getenv("AWS_S3_BUCKET", "xeno-oracle-data")),
        "objects": s3_stats.get("total_objects", 0),
        "size_mb": s3_stats.get("total_size_mb", 0)
    }

    # SES
    ses = get_ses_client()
    ses_sender = os.getenv("AWS_SES_SENDER_EMAIL", "")
    ses_enabled = os.getenv("AWS_SES_ENABLED", "false").lower() == "true"
    ses_info = {
        "connected": ses is not None and bool(ses_sender),
        "sender": ses_sender if ses_sender else None,
        "enabled": ses_enabled
    }

    # SNS
    sns_arn = os.getenv("AWS_SNS_TOPIC_ARN", "")
    sns_info = {
        "connected": get_sns_client() is not None and bool(sns_arn),
        "topic_arn": sns_arn if sns_arn else None
    }

    # CloudWatch
    cw = get_cloudwatch_client()
    cw_info = {
        "connected": cw is not None,
        "namespace": "XenoOracle"
    }

    # Secrets Manager
    sm = get_secrets_client()
    secret_name = os.getenv("AWS_SECRET_NAME", "xeno-oracle/production")
    sm_info = {
        "connected": sm is not None,
        "secret_name": secret_name
    }

    return {
        "s3": s3_info,
        "ses": ses_info,
        "sns": sns_info,
        "cloudwatch": cw_info,
        "secrets_manager": sm_info
    }
