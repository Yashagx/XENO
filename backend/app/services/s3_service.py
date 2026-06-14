import json
import os
import logging
from datetime import datetime
from app.services.aws_service import get_s3_client

logger = logging.getLogger(__name__)
BUCKET_NAME = os.getenv('AWS_S3_BUCKET', 'xeno-oracle-data')


async def export_campaign_to_s3(campaign_id: str, campaign_data: dict) -> str | None:
    """Export campaign report JSON to S3. Returns presigned URL or None if S3 unavailable."""
    s3 = get_s3_client()
    if not s3:
        return None
    try:
        key = f"campaigns/exports/{campaign_id}/report.json"
        body = json.dumps(campaign_data, indent=2, default=str)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body.encode('utf-8'),
            ContentType='application/json',
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600
        )
        logger.info(f"Campaign {campaign_id} exported to S3: {key}")
        return url
    except Exception as e:
        logger.warning(f"S3 export failed: {e}")
        return None


async def upload_customers_csv_to_s3(file_bytes: bytes, filename: str) -> str | None:
    """Upload customer CSV to S3 for audit trail."""
    s3 = get_s3_client()
    if not s3:
        return None
    try:
        key = f"customers/imports/{datetime.utcnow().isoformat()}/{filename}"
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=file_bytes, ContentType='text/csv')
        logger.info(f"CSV uploaded to S3: {key}")
        return key
    except Exception as e:
        logger.warning(f"S3 upload failed: {e}")
        return None


async def get_s3_storage_stats() -> dict:
    """Return bucket stats for the AWS status panel."""
    s3 = get_s3_client()
    if not s3:
        return {"connected": False}
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=1000)
        objects = response.get('Contents', [])
        return {
            "connected": True,
            "bucket": BUCKET_NAME,
            "total_objects": len(objects),
            "total_size_mb": round(sum(o['Size'] for o in objects) / 1024 / 1024, 2)
        }
    except Exception:
        return {"connected": False, "bucket": BUCKET_NAME}
