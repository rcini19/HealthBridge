from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def login_view(request):
    """User login view"""
    # Redirect authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            # Redirect admins/superusers to admin dashboard
            if request.user.is_superuser:
                return redirect("admin_dashboard")
            
            if not request.user.role_selected:
                return redirect("select_role")
            if request.user.is_donor:
                return redirect("dashboard:donor_dashboard")
            elif request.user.is_recipient:
                return redirect("dashboard:recipient_dashboard")
            return redirect("landing:home")
        except Exception as e:
            logger.error(f"Error checking user role: {str(e)}")
            return redirect("landing:home")
    
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            
            if not email or not password:
                return render(request, "login/login.html", {"error": "Email and password are required"})
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                logger.info(f"User {user.email} logged in successfully")
                
                # Check if user is admin/superuser first
                try:
                    # Redirect admins/superusers to admin dashboard
                    if user.is_superuser:
                        return redirect("admin_dashboard")
                    
                    # Check if user has selected their role
                    if not user.role_selected:
                        return redirect("select_role")
                    # Redirect to appropriate dashboard based on role
                    if user.is_donor:
                        return redirect("dashboard:donor_dashboard")
                    elif user.is_recipient:
                        return redirect("dashboard:recipient_dashboard")
                    return redirect("landing:home")
                except Exception as e:
                    logger.error(f"Error determining user dashboard: {str(e)}")
                    # Fallback to home if there's an issue
                    return redirect("landing:home")
            else:
                logger.warning(f"Failed login attempt for email: {email}")
                return render(request, "login/login.html", {"error": "Invalid credentials"})
        except Exception as e:
            logger.error(f"Login view error: {str(e)}")
            return render(request, "login/login.html", {"error": "An error occurred during login. Please try again."})
    
    return render(request, "login/login.html")


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect("landing:home")


class CustomPasswordResetView(PasswordResetView):
    template_name = 'login/password_reset.html'
    email_template_name = 'login/password_reset_email.html'
    success_url = reverse_lazy('login:password_reset_done')
    
    # Prevent duplicate email sends
    _email_sent = False
    
    def dispatch(self, request, *args, **kwargs):
        # Reset the flag for each request
        self._email_sent = False
        
        # Redirect authenticated users to their dashboard
        if request.user.is_authenticated:
            if not request.user.role_selected:
                return redirect("select_role")
            if request.user.is_donor:
                return redirect("dashboard:donor_dashboard")
            elif request.user.is_recipient:
                return redirect("dashboard:recipient_dashboard")
            return redirect("landing:home")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Override to add error handling and prevent worker timeout"""
        # Prevent duplicate sends
        if self._email_sent:
            logger.warning("Duplicate email send attempt detected - skipping")
            return redirect(self.success_url)
        
        # Check if email is configured (works for both SMTP and API backends)
        import os
        email_configured = False
        
        # Check for Brevo API configuration
        if os.getenv('BREVO_API_KEY'):
            email_configured = True
            backend_name = "Brevo API"
        # Check for Resend API configuration
        elif os.getenv('RESEND_API_KEY'):
            email_configured = True
            backend_name = "Resend API"
        # Check for SMTP configuration
        elif settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            email_configured = True
            backend_name = f"SMTP ({settings.EMAIL_HOST})"
        else:
            backend_name = "Console (no-op)"
        
        if not email_configured:
            logger.warning("Email credentials not fully configured - using console backend")
        
        try:
            # Log attempt (without sensitive info)
            logger.info(f"Attempting password reset email via {backend_name}")
            
            # Mark as sent before attempting
            self._email_sent = True
            
            # Try to send the email with timeout protection
            response = super().form_valid(form)
            logger.info(f"✓ Password reset email sent successfully via {backend_name}")
            return response
            
        except Exception as e:
            # Log the error but don't expose it to user
            logger.error(f"Password reset email failed: {type(e).__name__}: {str(e)}")
            # Still redirect to success page (security - don't reveal if email exists)
            return redirect(self.success_url)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'login/password_reset_done.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to their dashboard
        if request.user.is_authenticated:
            if not request.user.role_selected:
                return redirect("select_role")
            if request.user.is_donor:
                return redirect("dashboard:donor_dashboard")
            elif request.user.is_recipient:
                return redirect("dashboard:recipient_dashboard")
            return redirect("landing:home")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'login/password_reset_confirm.html'
    success_url = reverse_lazy('login:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'login/password_reset_complete.html'
