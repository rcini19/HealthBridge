from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/', views.get_notifications, name='get_notifications'),
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('api/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # Notification page
    path('', views.notifications_page, name='notifications_page'),
]
