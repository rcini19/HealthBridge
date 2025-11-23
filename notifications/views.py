"""
Notification views for HealthBridge
Handles notification display, marking as read, and notification count
"""

import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Notification

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get all notifications for the current user"""
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        # Paginate results
        page_number = request.GET.get('page', 1)
        paginator = Paginator(notifications, 10)  # 10 notifications per page
        page_obj = paginator.get_page(page_number)
        
        notifications_data = [
            {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'time_ago': notif.time_ago,
                'donation_id': notif.donation_id,
                'request_id': notif.request_id,
            }
            for notif in page_obj
        ]
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_count': paginator.count,
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
        })
    except Exception as e:
        logger.error(f'Error fetching notifications: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """Get count of unread notifications"""
    try:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({
            'success': True,
            'count': count
        })
    except Exception as e:
        logger.error(f'Error getting unread count: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)
    except Exception as e:
        logger.error(f'Error marking notification as read: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    try:
        from django.utils import timezone
        
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} notifications marked as read',
            'count': updated_count
        })
    except Exception as e:
        logger.error(f'Error marking all notifications as read: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def notifications_page(request):
    """Render the notifications page"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate
    page_number = request.GET.get('page', 1)
    paginator = Paginator(notifications, 15)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    
    return render(request, 'healthbridge_app/notifications.html', context)
