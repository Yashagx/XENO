"""
AWS Service wrapper. ALL methods are graceful-fallback:
if boto3 client init fails (no credentials), log warning and return None.
The app continues normally without AWS.
"""
import boto3
import logging
import os
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


def get_s3_client():
    try:
        client = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        # Test connectivity
        return client
    except Exception as e:
        logger.warning(f"AWS S3 client unavailable: {e}")
        return None


def get_ses_client():
    try:
        return boto3.client(
            'ses',
            region_name=os.getenv('AWS_SES_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        logger.warning(f"AWS SES client unavailable: {e}")
        return None


def get_sns_client():
    try:
        return boto3.client(
            'sns',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        logger.warning(f"AWS SNS client unavailable: {e}")
        return None


def get_cloudwatch_client():
    try:
        return boto3.client(
            'cloudwatch',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        logger.warning(f"AWS CloudWatch client unavailable: {e}")
        return None


def get_secrets_client():
    try:
        return boto3.client(
            'secretsmanager',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        logger.warning(f"AWS Secrets Manager client unavailable: {e}")
        return None
