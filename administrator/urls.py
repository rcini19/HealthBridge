from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve-donation/<int:donation_id>/', views.approve_donation, name='approve_donation'),
    path('reject-donation/<int:donation_id>/', views.reject_donation, name='reject_donation'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
]
