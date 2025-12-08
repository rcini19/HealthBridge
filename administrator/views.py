from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
import logging

from donations.models import Donation
from requests.models import MedicineRequest
from notifications.models import Notification

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is a superuser/admin"""
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin, login_url='/login/')
def admin_dashboard(request):
    """Main admin dashboard showing pending approvals and statistics"""
    
    # Get pending items
    pending_donations = Donation.objects.filter(
        approval_status=Donation.ApprovalStatus.PENDING
    ).select_related('donor').order_by('-donated_at')
    
    pending_requests = MedicineRequest.objects.filter(
        approval_status=MedicineRequest.ApprovalStatus.PENDING
    ).select_related('recipient', 'matched_donation__donor').order_by('-created_at')
    
    # Get statistics
    total_donations = Donation.objects.count()
    approved_donations = Donation.objects.filter(
        approval_status=Donation.ApprovalStatus.APPROVED
    ).count()
    
    total_requests = MedicineRequest.objects.count()
    approved_requests = MedicineRequest.objects.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED
    ).count()
    
    # Get recent approvals
    recent_approved_donations = Donation.objects.filter(
        approval_status=Donation.ApprovalStatus.APPROVED
    ).select_related('donor', 'reviewed_by').order_by('-reviewed_at')[:5]
    
    recent_approved_requests = MedicineRequest.objects.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED
    ).select_related('recipient', 'reviewed_by').order_by('-reviewed_at')[:5]
    
    context = {
        'pending_donations': pending_donations,
        'pending_requests': pending_requests,
        'pending_donations_count': pending_donations.count(),
        'pending_requests_count': pending_requests.count(),
        
        'total_donations': total_donations,
        'approved_donations': approved_donations,
        
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        
        'recent_approved_donations': recent_approved_donations,
        'recent_approved_requests': recent_approved_requests,
    }
    
    return render(request, 'healthbridge_app/admin_dashboard.html', context)


@user_passes_test(is_admin, login_url='/login/')
def approve_donation(request, donation_id):
    """Approve a donation"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    if request.method == 'POST':
        try:
            donation.approval_status = Donation.ApprovalStatus.APPROVED
            donation.reviewed_by = request.user
            donation.reviewed_at = timezone.now()
            donation.save()
            
            # Create notification for donor
            if donation.donor:
                Notification.objects.create(
                    user=donation.donor,
                    notification_type=Notification.Type.DONATION_APPROVED,
                    title='Donation Approved! ✅',
                    message=f'Your donation of {donation.quantity}x {donation.name} has been approved and is now available for recipients to request. Approved on {timezone.now().strftime("%B %d, %Y at %I:%M %p")}.',
                    donation_id=donation.id
                )
            
            messages.success(request, f'Donation "{donation.name}" has been approved!')
            logger.info(f'Admin {request.user.email} approved donation {donation.tracking_code}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Donation approved!'})
            
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error approving donation {donation_id}: {str(e)}')
            messages.error(request, 'An error occurred while approving the donation.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='/login/')
def reject_donation(request, donation_id):
    """Reject a donation"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    if request.method == 'POST':
        try:
            reason = request.POST.get('reason', '').strip()
            
            if not reason:
                messages.error(request, 'Please provide a reason for rejection.')
                return redirect('admin_dashboard')
            
            # Store donation info before deletion
            donation_name = donation.name
            donation_quantity = donation.quantity
            donor_user = donation.donor
            tracking_code = donation.tracking_code
            
            # Create notification for donor before deleting
            if donor_user:
                Notification.objects.create(
                    user=donor_user,
                    notification_type=Notification.Type.DONATION_REJECTED,
                    title='Donation Rejected ❌',
                    message=f'Your donation of {donation_quantity}x {donation_name} was rejected and removed. Reason: {reason}'
                )
            
            # Delete the donation from database
            donation.delete()
            
            messages.warning(request, f'Donation "{donation_name}" has been rejected and deleted.')
            logger.info(f'Admin {request.user.email} rejected and deleted donation {tracking_code}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Donation rejected!'})
            
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error rejecting donation {donation_id}: {str(e)}')
            messages.error(request, 'An error occurred while rejecting the donation.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='/login/')
def approve_request(request, request_id):
    """Approve a medicine request with optional claim ready date"""
    medicine_request = get_object_or_404(MedicineRequest, id=request_id)
    
    if request.method == 'POST':
        try:
            claim_date_str = request.POST.get('claim_ready_date', '').strip()
            
            medicine_request.approval_status = MedicineRequest.ApprovalStatus.APPROVED
            medicine_request.reviewed_by = request.user
            medicine_request.reviewed_at = timezone.now()
            
            # Set claim ready date if provided
            claim_date = None
            if claim_date_str:
                try:
                    claim_date = date.fromisoformat(claim_date_str)
                    medicine_request.claim_ready_date = claim_date
                except ValueError:
                    messages.warning(request, 'Invalid date format. Request approved without claim date.')
            
            medicine_request.save()
            
            # Create notification for recipient
            if medicine_request.recipient:
                if claim_date:
                    message = f'Your request for {medicine_request.quantity}x {medicine_request.medicine_name} has been approved! You can claim it on {claim_date.strftime("%B %d, %Y")}.'
                else:
                    message = f'Your request for {medicine_request.quantity}x {medicine_request.medicine_name} has been approved! Contact the clinic for claim details.'
                
                Notification.objects.create(
                    user=medicine_request.recipient,
                    notification_type=Notification.Type.REQUEST_APPROVED,
                    title='Request Approved! ✅',
                    message=message,
                    request_id=medicine_request.id
                )
            
            # Notify donor that their medicine request has been approved and must deliver by deadline
            if medicine_request.matched_donation and medicine_request.matched_donation.donor:
                recipient_name = medicine_request.recipient.get_full_name() or medicine_request.recipient.username
                
                if claim_date:
                    donor_message = (
                        f'🚨 DELIVERY REQUIRED: The request for {medicine_request.quantity}x {medicine_request.medicine_name} '
                        f'from {recipient_name} has been approved by admin. '
                        f'\n\n⚠️ YOU MUST DELIVER THIS MEDICINE ON OR BEFORE {claim_date.strftime("%B %d, %Y")}.'
                        f'\n\nRecipient Contact: {medicine_request.recipient.email}'
                        f'\nTracking Code: {medicine_request.tracking_code}'
                        f'\n\nPlease coordinate with the recipient to arrange delivery.'
                    )
                    notification_title = f'⚠️ Delivery Required by {claim_date.strftime("%b %d")} - Action Needed!'
                else:
                    donor_message = (
                        f'Good news! The request for {medicine_request.quantity}x {medicine_request.medicine_name} '
                        f'from {recipient_name} has been approved by admin. '
                        f'\n\nPlease deliver this medicine as soon as possible.'
                        f'\nRecipient Contact: {medicine_request.recipient.email}'
                        f'\nTracking Code: {medicine_request.tracking_code}'
                        f'\n\nCoordinate with the recipient for delivery arrangements.'
                    )
                    notification_title = 'Request Approved - Delivery Required 📦'
                
                Notification.objects.create(
                    user=medicine_request.matched_donation.donor,
                    notification_type=Notification.Type.REQUEST_APPROVED,
                    title=notification_title,
                    message=donor_message,
                    request_id=medicine_request.id,
                    donation_id=medicine_request.matched_donation.id
                )
            
            messages.success(request, f'Request for "{medicine_request.medicine_name}" has been approved!')
            logger.info(f'Admin {request.user.email} approved request {medicine_request.tracking_code}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Request approved!'})
            
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error approving request {request_id}: {str(e)}')
            messages.error(request, 'An error occurred while approving the request.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='/login/')
def reject_request(request, request_id):
    """Reject a medicine request"""
    medicine_request = get_object_or_404(MedicineRequest, id=request_id)
    
    if request.method == 'POST':
        try:
            reason = request.POST.get('reason', '').strip()
            
            if not reason:
                messages.error(request, 'Please provide a reason for rejection.')
                return redirect('admin_dashboard')
            
            # Store request info before deletion
            medicine_name = medicine_request.medicine_name
            quantity = medicine_request.quantity
            recipient_user = medicine_request.recipient
            tracking_code = medicine_request.tracking_code
            matched_donation = medicine_request.matched_donation
            
            # Create notification for recipient before deleting
            if recipient_user:
                Notification.objects.create(
                    user=recipient_user,
                    notification_type=Notification.Type.REQUEST_REJECTED,
                    title='Request Rejected ❌',
                    message=f'Your request for {quantity}x {medicine_name} was rejected and removed. Reason: {reason}'
                )
            
            # If the request was matched to a donation, set that donation back to AVAILABLE
            if matched_donation:
                matched_donation.status = Donation.Status.AVAILABLE
                matched_donation.save()
            
            # Delete the request from database
            medicine_request.delete()
            
            messages.warning(request, f'Request for "{medicine_name}" has been rejected and deleted.')
            logger.info(f'Admin {request.user.email} rejected and deleted request {tracking_code}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Request rejected!'})
            
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error rejecting request {request_id}: {str(e)}')
            messages.error(request, 'An error occurred while rejecting the request.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='/login/')
def get_donation_details(request, donation_id):
    """API endpoint to get full donation details"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    donor = donation.donor
    data = {
        'donation': {
            'id': donation.id,
            'name': donation.name,
            'quantity': donation.quantity,
            'expiry_date': donation.expiry_date.strftime('%B %d, %Y'),
            'tracking_code': donation.tracking_code,
            'status': donation.get_status_display(),
            'approval_status': donation.get_approval_status_display(),
            'donated_at': donation.donated_at.strftime('%B %d, %Y at %I:%M %p'),
            'notes': donation.notes or 'No additional notes',
            'image_url': donation.image.url if donation.image else None,
            'days_until_expiry': donation.days_until_expiry,
        },
        'donor': {
            'id': donor.id if donor else None,
            'full_name': donor.get_full_name() if donor else 'Anonymous',
            'username': donor.username if donor else 'N/A',
            'email': donor.email if donor else 'N/A',
            'phone': donor.phone_number or 'Not provided',
            'address': donor.address or 'Not provided',
            'user_type': donor.get_user_type_display() if donor and donor.user_type else 'N/A',
            'date_joined': donor.date_joined.strftime('%B %d, %Y') if donor else 'N/A',
        }
    }
    
    return JsonResponse(data)


@user_passes_test(is_admin, login_url='/login/')
def get_request_details(request, request_id):
    """API endpoint to get full request details"""
    medicine_request = get_object_or_404(MedicineRequest, id=request_id)
    
    recipient = medicine_request.recipient
    matched_donation = medicine_request.matched_donation
    
    data = {
        'request': {
            'id': medicine_request.id,
            'medicine_name': medicine_request.medicine_name,
            'quantity': medicine_request.quantity,
            'urgency': medicine_request.get_urgency_display(),
            'urgency_class': medicine_request.urgency,
            'reason': medicine_request.reason or 'No reason provided',
            'notes': medicine_request.notes or 'No additional notes',
            'tracking_code': medicine_request.tracking_code,
            'status': medicine_request.get_status_display(),
            'approval_status': medicine_request.get_approval_status_display(),
            'created_at': medicine_request.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'claim_ready_date': medicine_request.claim_ready_date.strftime('%B %d, %Y') if medicine_request.claim_ready_date else 'Not set',
            'days_since_request': medicine_request.days_since_request,
        },
        'recipient': {
            'id': recipient.id,
            'full_name': recipient.get_full_name(),
            'username': recipient.username,
            'email': recipient.email,
            'phone': recipient.phone_number or 'Not provided',
            'address': recipient.address or 'Not provided',
            'user_type': recipient.get_user_type_display() if recipient.user_type else 'N/A',
            'date_joined': recipient.date_joined.strftime('%B %d, %Y'),
        },
        'matched_donation': None
    }
    
    if matched_donation:
        donor = matched_donation.donor
        data['matched_donation'] = {
            'id': matched_donation.id,
            'name': matched_donation.name,
            'quantity': matched_donation.quantity,
            'tracking_code': matched_donation.tracking_code,
            'image_url': matched_donation.image.url if matched_donation.image else None,
            'donor_name': donor.get_full_name() if donor else 'Anonymous',
            'donor_email': donor.email if donor else 'N/A',
            'donor_phone': donor.phone_number if donor else 'Not provided',
        }
    
    return JsonResponse(data)
