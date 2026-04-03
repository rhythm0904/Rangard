"""
app/services/email.py
─────────────────────
Email notification service.

Sends instant alerts when threats are detected, with:
  • Threat severity and confidence score
  • Affected filename
  • Direct link to the recovery/quarantine dashboard
  • HTML email with nice formatting

Supports two backends:
  1. Gmail SMTP (free, simple, reliable)
  2. SendGrid (enterprise, higher limits)

Currently uses: Gmail SMTP via rangard.safe@gmail.com
"""

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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


# ── Email verification templates ──────────────────────────────────────────────

EMAIL_VERIFICATION_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #6e40c9 0%, #1f6feb 100%); padding: 40px 30px; text-align: center; }}
    .header h1 {{ margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; }}
    .header p {{ margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500; }}
    .body {{ padding: 40px 30px; }}
    .body p {{ margin: 15px 0; font-size: 15px; color: #555; }}
    .body h2 {{ margin: 25px 0 15px; font-size: 18px; color: #2c3e50; font-weight: 700; }}
    .button {{ display: inline-block; padding: 14px 36px; background: linear-gradient(135deg, #6e40c9, #5a2fa8); color: #ffffff; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 16px; margin: 20px 0; transition: transform 0.2s; }}
    .button:hover {{ transform: translateY(-2px); }}
    .link-box {{ background: #f8f9fa; border: 1px solid #e0e3e8; border-radius: 6px; padding: 15px; margin: 20px 0; word-break: break-all; }}
    .link-box p {{ margin: 0; font-size: 13px; color: #999; }}
    .link {{ font-family: monospace; color: #6e40c9; font-weight: 600; display: block; margin-top: 8px; }}
    .benefits {{ background: #f0f4ff; border-left: 4px solid #6e40c9; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    .benefits h3 {{ margin: 0 0 10px; color: #2c3e50; font-size: 14px; }}
    .benefits li {{ margin: 6px 0; padding-left: 20px; }}
    .security-note {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    .security-note p {{ margin: 0; font-size: 14px; color: #856404; }}
    .footer {{ background: #f8f9fa; border-top: 1px solid #e0e3e8; padding: 25px 30px; text-align: center; font-size: 12px; color: #999; }}
    .footer p {{ margin: 6px 0; }}
    .divider {{ height: 1px; background: #e0e3e8; margin: 20px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🛡️ Welcome to RANGARD</h1>
      <p>Verify Your Email to Complete Registration</p>
    </div>
    
    <div class="body">
      <p><strong>Hello,</strong></p>
      
      <p>Thank you for registering with RANGARD — the advanced AI-powered ransomware detection system. We're excited to help you protect your files from threats.</p>
      
      <h2>Verify Your Email Address</h2>
      <p>To activate your account and start using RANGARD, please verify your email address by clicking the button below:</p>
      
      <center>
        <a href="{verification_link}" class="button">✓ Verify Email Address</a>
      </center>
      
      <p style="text-align: center; margin-top: 10px; font-size: 13px; color: #999;">
        (If the button doesn't work, copy and paste the link below into your browser)
      </p>
      
      <div class="link-box">
        <p>Verification Link:</p>
        <span class="link">{verification_link}</span>
      </div>
      
      <div class="benefits">
        <h3>✨ What You'll Get After Verification:</h3>
        <ul style="list-style: none; margin: 0; padding: 0;">
          <li>✓ Instant threat detection alerts for uploaded files</li>
          <li>✓ AI-powered ransomware scanning and analysis</li>
          <li>✓ Automatic file quarantine for suspicious items</li>
          <li>✓ Detailed threat reports and recommendations</li>
        </ul>
      </div>
      
      <div class="security-note">
        <p><strong>⚠️ Security Note:</strong> This verification link expires in 24 hours. If you did not create this account, please disregard this email or contact our support team.</p>
      </div>
      
      <p style="font-size: 14px; color: #666; margin-top: 20px;">
        <strong>Need help?</strong> If you experience any issues with verification, please check:
      </p>
      <ul style="margin: 10px 0 20px 20px; font-size: 14px; color: #666;">
        <li>This email wasn't accidentally marked as spam</li>
        <li>The link hasn't expired (valid for 24 hours)</li>
        <li>Your email address is correct</li>
      </ul>
    </div>
    
    <div class="footer">
      <p><strong>RANGARD Security</strong> — Advanced Ransomware Detection & Prevention</p>
      <p style="margin-top: 12px;">© 2026 RANGARD. All rights reserved.</p>
      <p style="margin-top: 8px;">This is an automated message. Please do not reply to this email.</p>
    </div>
  </div>
</body>
</html>
"""

EMAIL_VERIFICATION_TEXT = """
═══════════════════════════════════════════════════════════════
                    WELCOME TO RANGARD
                   Email Verification Required
═══════════════════════════════════════════════════════════════

Hello,

Thank you for registering with RANGARD — the advanced AI-powered ransomware detection system.

VERIFY YOUR EMAIL ADDRESS
──────────────────────────

To activate your account and start using RANGARD, please verify your email by visiting:

{verification_link}


WHAT YOU'LL GET AFTER VERIFICATION
──────────────────────────────────

✓ Instant threat detection alerts for uploaded files
✓ AI-powered ransomware scanning and analysis
✓ Automatic file quarantine for suspicious items  
✓ Detailed threat reports and recommendations


IMPORTANT INFORMATION
─────────────────────

⏰ Expiration: This link is valid for 24 hours
🔒 Security: If you did not create this account, please disregard this email
❓ Questions: Contact our support team if you need help

---

This is an automated message from RANGARD Security.
Please do not reply to this email.

© 2026 RANGARD. All rights reserved.
═══════════════════════════════════════════════════════════════

---
RANGARD Security
"""




class EmailService:
    """
    Email service using Gmail SMTP.
    Simple, reliable, no API key complexity.
    """

    def __init__(self):
        self.gmail_user = settings.EMAIL_FROM  # rangard.safe@gmail.com
        self.gmail_password = settings.GMAIL_APP_PASSWORD  # Get from env
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self._verify_config()

    def _verify_config(self):
        """Check Gmail credentials are configured."""
        if not self.gmail_user or not self.gmail_password:
            logger.warning("[Email] Gmail credentials not configured")
            return
        
        if "@gmail.com" not in self.gmail_user:
            logger.warning(f"[Email] Email is not a Gmail address: {self.gmail_user}")
            return
            
        logger.info(f"[Email] Gmail SMTP ready ({self.gmail_user})")

    def _send_via_gmail(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> tuple[bool, Optional[str]]:
        """Send email via Gmail SMTP with proper headers for deliverability."""
        try:
            from datetime import datetime
            
            # Create message with more robust headers
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"RANGARD Security <{self.gmail_user}>"
            msg["To"] = to_email
            msg["Reply-To"] = self.gmail_user
            msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
            msg["Message-ID"] = f"<rangard-{datetime.utcnow().timestamp()}@rangard.io>"
            msg["X-Mailer"] = "RANGARD v1.0"
            msg["MIME-Version"] = "1.0"
            msg["X-Priority"] = "2" # Normal priority
            msg["X-MSMail-Priority"] = "Normal"

            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Connect to Gmail SMTP and send
            logger.info(f"[Email] Connecting to {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            try:
                logger.info("[Email] Starting TLS...")
                server.starttls()
                logger.info("[Email] Logging in...")
                server.login(self.gmail_user, self.gmail_password)
                logger.info(f"[Email] Sending to {to_email}...")
                
                # Use sendmail with explicit sender and recipient
                result = server.sendmail(self.gmail_user, [to_email], msg.as_string())
                
                logger.info(f"[Email] ✅ Email sent to {to_email} via Gmail SMTP")
                logger.info(f"[Email] Subject: {subject}")
                logger.info(f"[Email] From: {self.gmail_user}")
                logger.info(f"[Email] To: {to_email}")
                return True, None
            finally:
                try:
                    server.quit()
                except:
                    server.close()

        except smtplib.SMTPAuthenticationError as e:
            error = f"Gmail authentication failed: {str(e)}"
            logger.error(f"[Email] ❌ {error}")
            return False, error
        except smtplib.SMTPException as e:
            error = f"SMTP error: {str(e)}"
            logger.error(f"[Email] ❌ {error}")
            return False, error
        except TimeoutError as e:
            error = f"Connection timeout: {str(e)}"
            logger.error(f"[Email] ❌ {error}")
            return False, error
        except Exception as e:
            error = str(e)
            logger.error(f"[Email] ❌ Failed to send email: {error}")
            import traceback
            logger.error(f"[Email] Traceback: {traceback.format_exc()}")
            return False, error

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
    ) -> tuple[bool, Optional[str]]:
        """
        Send a threat detection email via Gmail SMTP.
        Returns tuple of (success: bool, error_message: Optional[str])
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

        # Log in development mode
        if settings.APP_ENV == "development":
            logger.info(f"[Email] Sending threat alert to {to_email}: {subject}")

        return self._send_via_gmail(to_email, subject, html_body, text_body)

    def send_email_verification(
        self,
        to_email: str,
        verification_link: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email verification link to a new user via Gmail SMTP.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        subject = "Verify Your Email - RANGARD"
        html_body = EMAIL_VERIFICATION_HTML.format(verification_link=verification_link)
        text_body = EMAIL_VERIFICATION_TEXT.format(verification_link=verification_link)

        # Log in development mode
        if settings.APP_ENV == "development":
            logger.info(f"[Email] Sending verification email to {to_email}")

        return self._send_via_gmail(to_email, subject, html_body, text_body)


# ── Singleton ─────────────────────────────────────────────────────────────────

_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
