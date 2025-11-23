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
    ).select_related('recipient').order_by('-created_at')
    
    # Get statistics
    total_donations = Donation.objects.count()
    approved_donations = Donation.objects.filter(
        approval_status=Donation.ApprovalStatus.APPROVED
    ).count()
    rejected_donations = Donation.objects.filter(
        approval_status=Donation.ApprovalStatus.REJECTED
    ).count()
    
    total_requests = MedicineRequest.objects.count()
    approved_requests = MedicineRequest.objects.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED
    ).count()
    rejected_requests = MedicineRequest.objects.filter(
        approval_status=MedicineRequest.ApprovalStatus.REJECTED
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
        'rejected_donations': rejected_donations,
        
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        
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
            
            donation.approval_status = Donation.ApprovalStatus.REJECTED
            donation.reviewed_by = request.user
            donation.reviewed_at = timezone.now()
            donation.rejection_reason = reason
            donation.save()
            
            # Create notification for donor
            if donation.donor:
                Notification.objects.create(
                    user=donation.donor,
                    notification_type=Notification.Type.DONATION_REJECTED,
                    title='Donation Rejected ❌',
                    message=f'Your donation of {donation.quantity}x {donation.name} was rejected. Reason: {reason}',
                    donation_id=donation.id
                )
            
            messages.warning(request, f'Donation "{donation.name}" has been rejected.')
            logger.info(f'Admin {request.user.email} rejected donation {donation.tracking_code}')
            
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
            
            medicine_request.approval_status = MedicineRequest.ApprovalStatus.REJECTED
            medicine_request.reviewed_by = request.user
            medicine_request.reviewed_at = timezone.now()
            medicine_request.rejection_reason = reason
            medicine_request.save()
            
            # Create notification for recipient
            if medicine_request.recipient:
                Notification.objects.create(
                    user=medicine_request.recipient,
                    notification_type=Notification.Type.REQUEST_REJECTED,
                    title='Request Rejected ❌',
                    message=f'Your request for {medicine_request.quantity}x {medicine_request.medicine_name} was rejected. Reason: {reason}',
                    request_id=medicine_request.id
                )
            
            messages.warning(request, f'Request for "{medicine_request.medicine_name}" has been rejected.')
            logger.info(f'Admin {request.user.email} rejected request {medicine_request.tracking_code}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Request rejected!'})
            
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error rejecting request {request_id}: {str(e)}')
            messages.error(request, 'An error occurred while rejecting the request.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('admin_dashboard')
