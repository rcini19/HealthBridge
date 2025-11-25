from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    # API endpoints
    path("api/medicine-autocomplete/", views.medicine_autocomplete, name="medicine_autocomplete"),

    path("search/", views.medicine_search, name="medicine_search"),
    path("donate/", views.donate_medicine, name="donate_medicine"),

    # Donor tracking
    path("requests/", views.my_donations, name="request_list"),
    path("requests/<int:pk>/", views.donation_detail, name="request_detail"),
    path("donations/<int:pk>/delete/", views.delete_donation, name="delete_donation"),
    
    # Recipient delete function (still needed here)
    path("recipient/requests/<int:pk>/delete/", views.delete_medicine_request, name="delete_medicine_request"),

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='healthbridge_app/password_reset.html',
        email_template_name='healthbridge_app/password_reset_email.html'
    ), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='healthbridge_app/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='healthbridge_app/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='healthbridge_app/password_reset_complete.html'
    ), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)