"""
app/services/email.py
─────────────────────
Email notification service.

Sends instant alerts when threats are detected, with:
  • Threat severity and confidence score
  • Affected filename
  • Direct link to the recovery/quarantine dashboard
  • HTML email with nice formatting

Uses SendGrid's free tier (100 emails/day).
Falls back to console logging if SendGrid isn't configured (dev mode).
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# ── Email templates ───────────────────────────────────────────────────────────

THREAT_ALERT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body      {{ font-family: Arial, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 0; }}
    .container{{ max-width: 600px; margin: 40px auto; background: #161b22; border-radius: 12px;
                 border: 1px solid #30363d; overflow: hidden; }}
    .header   {{ background: linear-gradient(135deg, #6e40c9, #1f6feb); padding: 32px 40px; }}
    .header h1{{ margin: 0; color: #fff; font-size: 24px; }}
    .header p {{ margin: 6px 0 0; color: rgba(255,255,255,0.8); font-size: 14px; }}
    .body     {{ padding: 32px 40px; }}
    .badge    {{ display: inline-block; padding: 4px 12px; border-radius: 20px;
                 font-size: 13px; font-weight: bold; text-transform: uppercase; }}
    .critical {{ background: #7d1a1a; color: #fca5a5; }}
    .high     {{ background: #7c2d12; color: #fdba74; }}
    .medium   {{ background: #713f12; color: #fde68a; }}
    .low      {{ background: #14532d; color: #86efac; }}
    .clean    {{ background: #166534; color: #bbf7d0; }}
    .detail   {{ background: #0d1117; border-radius: 8px; padding: 20px; margin: 20px 0;
                 border-left: 3px solid #6e40c9; }}
    .detail p {{ margin: 6px 0; font-size: 14px; color: #8b949e; }}
    .detail strong {{ color: #c9d1d9; }}
    .button   {{ display: inline-block; padding: 14px 28px; background: #6e40c9;
                 color: #fff; border-radius: 8px; text-decoration: none;
                 font-weight: bold; font-size: 15px; margin-top: 8px; }}
    .footer   {{ padding: 20px 40px; border-top: 1px solid #30363d;
                 font-size: 12px; color: #6e7681; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🛡️ RANGARD Security Alert</h1>
      <p>A potential threat was detected in your uploaded file</p>
    </div>
    <div class="body">
      <p>Hello {name},</p>
      <p>RANGARD has detected a <span class="badge {threat_class}">{threat_level}</span>
         threat in a file you uploaded.</p>

      <div class="detail">
        <p><strong>File:</strong> {filename}</p>
        <p><strong>Threat level:</strong> {threat_level_display}</p>
        <p><strong>Confidence:</strong> {confidence}%</p>
        <p><strong>Detected at:</strong> {detected_at}</p>
        <p><strong>Action taken:</strong> {action}</p>
        {patterns_html}
      </div>

      <p>The file has been automatically quarantined to prevent further spread.</p>

      <a href="{dashboard_url}" class="button">View in Dashboard →</a>
    </div>
    <div class="footer">
      <p>This alert was sent by RANGARD because a file you uploaded triggered our AI detection system.</p>
      <p>Scan ID: {scan_id}</p>
    </div>
  </div>
</body>
</html>
"""

THREAT_ALERT_TEXT = """
RANGARD Security Alert
───────────────────────────
Hello {name},

A {threat_level} threat was detected in your uploaded file.

File:         {filename}
Threat level: {threat_level_display}
Confidence:   {confidence}%
Detected at:  {detected_at}
Action taken: {action}

Detected patterns:
{patterns_text}

View your dashboard: {dashboard_url}

Scan ID: {scan_id}
"""


# ── Service ───────────────────────────────────────────────────────────────────

class EmailService:

    def __init__(self):
        self.client = None
        self._setup()

    def _setup(self):
        if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY.startswith("SG.XXX"):
            logger.info("[Email] No SendGrid key configured — emails will be logged only")
            return
        try:
            import sendgrid
            from sendgrid import SendGridAPIClient
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            logger.info("[Email] SendGrid connected")
        except ImportError:
            logger.warning("[Email] sendgrid package not installed")

    def send_threat_alert(
        self,
        to_email: str,
        to_name: str,
        filename: str,
        threat_level: str,
        confidence: float,
        patterns: list[str],
        scan_id: str,
        dashboard_url: str = "http://localhost:3000/dashboard",
    ) -> bool:
        """
        Send a threat detection email.
        Returns True on success, False on failure.
        """
        action_map = {
            "critical": "File quarantined immediately — URGENT action required",
            "high":     "File quarantined — review recommended",
            "medium":   "File quarantined — monitoring active",
            "low":      "File flagged — manual review suggested",
            "clean":    "No action required",
        }

        patterns_html = "".join(
            f"<p><strong>•</strong> {p}</p>" for p in patterns
        ) if patterns else "<p>No specific patterns noted</p>"

        patterns_text = "\n".join(f"  • {p}" for p in patterns) if patterns else "  • None"

        ctx = {
            "name":              to_name or to_email,
            "filename":          filename,
            "threat_level":      threat_level.upper(),
            "threat_level_display": threat_level.title(),
            "threat_class":      threat_level.lower(),
            "confidence":        round(confidence * 100, 1),
            "detected_at":       datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "action":            action_map.get(threat_level, "Under review"),
            "patterns_html":     patterns_html,
            "patterns_text":     patterns_text,
            "dashboard_url":     dashboard_url,
            "scan_id":           scan_id,
        }

        subject = f"[RANGARD] {threat_level.upper()} Threat Detected — {filename}"
        html_body = THREAT_ALERT_HTML.format(**ctx)
        text_body = THREAT_ALERT_TEXT.format(**ctx)

        # Always log in dev
        if settings.APP_ENV == "development":
            logger.info(f"[Email] WOULD SEND to {to_email}: {subject}")
            logger.debug(text_body)

        if self.client is None:
            return True  # dev mode — pretend it worked

        try:
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_body,
                plain_text_content=text_body,
            )
            response = self.client.send(message)
            success = response.status_code in (200, 202)
            if success:
                logger.info(f"[Email] Threat alert sent to {to_email} (status {response.status_code})")
            else:
                logger.error(f"[Email] Send failed: status {response.status_code}")
            return success

        except Exception as e:
            logger.error(f"[Email] Error sending to {to_email}: {e}")
            return False


# ── Singleton ─────────────────────────────────────────────────────────────────

_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
