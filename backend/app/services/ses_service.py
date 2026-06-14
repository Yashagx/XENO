import os
import logging
from app.services.aws_service import get_ses_client
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
SES_SENDER = os.getenv('AWS_SES_SENDER_EMAIL', '')


async def send_campaign_completion_email(
    marketer_email: str,
    campaign_name: str,
    stats: dict
) -> bool:
    """Send campaign completion summary email to marketer via SES."""
    ses = get_ses_client()
    if not ses or not SES_SENDER or not marketer_email:
        return False
    open_rate = stats.get('open_rate', 0)
    roi = stats.get('roi', 0)
    revenue = stats.get('revenue_inr', stats.get('converted', 0) * 1500)
    html_body = f"""
    <html><body style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #6366f1; padding: 24px; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0;">&#10022; Xeno Oracle</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0;">Campaign Intelligence Report</p>
      </div>
      <div style="background: white; padding: 24px; border: 1px solid #e5e7eb; border-radius: 0 0 12px 12px;">
        <h2 style="color: #111827;">Campaign Complete: {campaign_name}</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
          <tr style="background: #f9fafb;">
            <td style="padding: 12px; border: 1px solid #e5e7eb;">Open Rate</td>
            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold;">{open_rate:.1%}</td>
          </tr>
          <tr>
            <td style="padding: 12px; border: 1px solid #e5e7eb;">ROI</td>
            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold;">{roi:.1f}x</td>
          </tr>
          <tr style="background: #f0fdf4;">
            <td style="padding: 12px; border: 1px solid #e5e7eb;">Revenue Generated</td>
            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold; color: #16a34a;">&#8377;{revenue:,.0f}</td>
          </tr>
        </table>
        <p style="margin-top: 24px; color: #6b7280; font-size: 14px;">Powered by Xeno Oracle &middot; AI Marketing OS</p>
      </div>
    </body></html>
    """
    try:
        ses.send_email(
            Source=SES_SENDER,
            Destination={'ToAddresses': [marketer_email]},
            Message={
                'Subject': {'Data': f'Campaign Complete: {campaign_name} · {open_rate:.0%} open rate'},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        logger.info(f"SES email sent to {marketer_email} for campaign '{campaign_name}'")
        return True
    except ClientError as e:
        logger.warning(f"SES send failed: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.warning(f"SES send error: {e}")
        return False
