"""
Brevo (Sendinblue) email backend for Django
Uses Brevo's REST API instead of SMTP to bypass port blocking on Render.com
"""

import os
import logging
from typing import List, Optional
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
import httpx

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """
    Django email backend that uses Brevo's API instead of SMTP.
    
    This backend sends emails through Brevo's RESTful API, which works 
    on Render.com free tier since it uses standard HTTPS ports instead 
    of SMTP ports (which are blocked).
    
    Settings required:
    - BREVO_API_KEY: Your Brevo API key from https://app.brevo.com/settings/keys/api
    
    Usage in settings.py:
        EMAIL_BACKEND = 'HealthBridge.brevo_backend.BrevoEmailBackend'
        BREVO_API_KEY = os.getenv('BREVO_API_KEY')
        DEFAULT_FROM_EMAIL = 'your-email@yourdomain.com'
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.getenv('BREVO_API_KEY')
        if not self.api_key:
            logger.warning("BREVO_API_KEY not found in environment variables")
        self.api_url = "https://api.brevo.com/v3/smtp/email"
    
    def send_messages(self, email_messages: List[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number sent successfully.
        """
        if not self.api_key:
            logger.error("Cannot send email: BREVO_API_KEY not configured")
            return 0
        
        # Log how many messages are being sent
        logger.info(f"Brevo backend received {len(email_messages)} email message(s) to send")
        
        num_sent = 0
        for idx, message in enumerate(email_messages, 1):
            try:
                logger.info(f"Processing email {idx}/{len(email_messages)}: To={message.to}, Subject='{message.subject}'")
                if self._send_message(message):
                    num_sent += 1
            except Exception as e:
                logger.exception(f"Error sending email via Brevo: {e}")
                if not self.fail_silently:
                    raise
        
        logger.info(f"Brevo backend sent {num_sent}/{len(email_messages)} emails successfully")
        return num_sent
    
    def _send_message(self, message: EmailMessage) -> bool:
        """
        Send a single EmailMessage via Brevo API.
        Returns True if successful, False otherwise.
        """
        # Build recipient list
        to_recipients = [{"email": email, "name": email.split('@')[0]} 
                        for email in message.to]
        
        # Build email data for Brevo API
        from_name = os.getenv('BREVO_FROM_NAME', message.from_email.split('@')[0])
        email_data = {
            "sender": {
                "email": message.from_email,
                "name": from_name
            },
            "to": to_recipients,
            "subject": message.subject,
        }
        
        # Add CC if present
        if message.cc:
            email_data["cc"] = [{"email": email} for email in message.cc]
        
        # Add BCC if present
        if message.bcc:
            email_data["bcc"] = [{"email": email} for email in message.bcc]
        
        # Add reply-to if present
        if hasattr(message, 'reply_to') and message.reply_to:
            email_data["replyTo"] = {"email": message.reply_to[0]}
        
        # Handle HTML and text content
        if isinstance(message, EmailMultiAlternatives):
            # Check for HTML alternative
            html_content = None
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_content = content
                    break
            
            if html_content:
                email_data["htmlContent"] = html_content
            else:
                email_data["textContent"] = message.body
        else:
            # Plain text email
            email_data["textContent"] = message.body
        
        # Handle attachments
        if message.attachments:
            email_data["attachment"] = []
            for attachment in message.attachments:
                if isinstance(attachment, tuple):
                    # (filename, content, mimetype)
                    filename, content, mimetype = attachment
                    
                    # Convert content to base64 if it's bytes
                    import base64
                    if isinstance(content, bytes):
                        content_b64 = base64.b64encode(content).decode('utf-8')
                    else:
                        content_b64 = base64.b64encode(content.encode()).decode('utf-8')
                    
                    email_data["attachment"].append({
                        "name": filename,
                        "content": content_b64
                    })
        
        # Send the request to Brevo API
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.api_url,
                    json=email_data,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Email sent successfully via Brevo to {message.to}")
                    return True
                else:
                    logger.error(
                        f"Brevo API error (status {response.status_code}): {response.text}"
                    )
                    if not self.fail_silently:
                        raise Exception(f"Brevo API returned status {response.status_code}: {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Brevo API request timed out")
            if not self.fail_silently:
                raise
            return False
        except Exception as e:
            logger.exception(f"Error calling Brevo API: {e}")
            if not self.fail_silently:
                raise
            return False
