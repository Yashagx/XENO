import os
import json
import logging
from app.services.aws_service import get_secrets_client

logger = logging.getLogger(__name__)


async def load_secrets_from_aws() -> dict:
    """
    Attempt to load secrets from AWS Secrets Manager.
    Returns dict of secrets, or empty dict if unavailable.
    Secret name: xeno-oracle/production
    Secret value format: {"GROQ_API_KEY": "...", "JWT_SECRET": "..."}
    """
    client = get_secrets_client()
    if not client:
        return {}
    secret_name = os.getenv('AWS_SECRET_NAME', 'xeno-oracle/production')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(response['SecretString'])
        logger.info(f"Loaded {len(secrets)} secrets from AWS Secrets Manager")
        return secrets
    except Exception as e:
        logger.info(f"AWS Secrets Manager unavailable or secret not found: {e} — using environment variables")
        return {}
