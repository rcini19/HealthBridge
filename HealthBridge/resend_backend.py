"""
Custom email backend for Resend API
Uses HTTP API instead of SMTP to bypass port blocking on Render
"""
import os
import logging
import sys
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

# CRITICAL FIX: Your Django app is named 'requests' which shadows the Python requests package
# We need to ensure the real requests package is imported by resend, not your Django app

# Get the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Clean up any cached imports of the Django 'requests' app
modules_to_remove = []
for module_name in sys.modules:
    if module_name == 'requests' or module_name.startswith('requests.'):
        module = sys.modules[module_name]
        # Check if it's the Django app by looking at its file path
        if hasattr(module, '__file__') and module.__file__:
            if project_root in module.__file__:
                modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    del sys.modules[module_name]

# Temporarily manipulate sys.path to ensure site-packages is prioritized
original_sys_path = sys.path.copy()
# Move all paths containing the project root to the end
project_paths = [p for p in sys.path if project_root in os.path.abspath(p)]
other_paths = [p for p in sys.path if project_root not in os.path.abspath(p)]
sys.path = other_paths + project_paths

# Import resend (which needs the real requests package)
import resend

# Restore original sys.path
sys.path = original_sys_path

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend that uses Resend's HTTP API instead of SMTP.
    Works on Render free tier since it uses HTTPS (port 443) instead of SMTP ports.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        
        if not self.api_key:
            if not fail_silently:
                raise ValueError("RESEND_API_KEY not found in settings")
            logger.warning("RESEND_API_KEY not configured")
        else:
            resend.api_key = self.api_key
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        
        if not self.api_key:
            logger.error("Cannot send emails: RESEND_API_KEY not configured")
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email via Resend: {str(e)}")
                if not self.fail_silently:
                    raise
        
        return num_sent
    
    def _send(self, message):
        """Send a single email message via Resend API"""
        if not message.recipients():
            return False
        
        try:
            # Prepare email data for Resend API
            params = {
                "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                "to": message.to,
                "subject": message.subject,
            }
            
            # Add CC and BCC if present
            if message.cc:
                params["cc"] = message.cc
            if message.bcc:
                params["bcc"] = message.bcc
            
            # Handle HTML and plain text content
            if message.content_subtype == 'html':
                params["html"] = message.body
            else:
                params["text"] = message.body
            
            # If both HTML and text alternatives exist
            if hasattr(message, 'alternatives') and message.alternatives:
                for alternative_content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        params["html"] = alternative_content
            
            # Send via Resend API
            response = resend.Emails.send(params)
            
            if response and response.get('id'):
                logger.info(f"Email sent successfully via Resend: {response.get('id')}")
                return True
            else:
                logger.error(f"Resend API returned unexpected response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email via Resend: {str(e)}")
            if not self.fail_silently:
                raise
            return False
