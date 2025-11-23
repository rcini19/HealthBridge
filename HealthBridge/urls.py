"""
URL configuration for HealthBridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from healthbridge_app import views as hb_views

urlpatterns = [
    # Admin Dashboard & Approvals (must come before Django admin!)
    path('admin-dashboard/', include('administrator.urls')),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Role selection (one-time for new users)
    path('select-role/', hb_views.select_role, name='select_role'),
    
    # Notification endpoints
    path('notifications/', include('notifications.urls')),
    
    # Modular apps
    path('', include('landing.urls')),  # Landing page at root
    path('login/', include('login.urls')),  # Login, logout, and password reset
    path('register/', include('registration.urls')),  # Registration
    path('dashboard/', include('dashboard.urls')),  # Dashboards
    path('profile/', include('profile.urls')),  # User profile
    path('donations/', include('donations.urls')),  # Donations
    path('requests/', include('requests.urls')),  # Medicine requests
]

# Custom error handlers
handler404 = 'HealthBridge.views.custom_404'
handler500 = 'HealthBridge.views.custom_500'

# Note: Media files are served from Supabase Storage (cloud), not locally
# No need for local media serving with Supabase Storage backend
