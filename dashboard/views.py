from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
import logging

from donations.models import Donation, ExpiryAlert
from requests.models import MedicineRequest

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Unified dashboard view combining donor and recipient features"""
    context = {}
    
    # ===== DONOR STATISTICS =====
    total_donations = Donation.objects.filter(donor=request.user).count()
    available_donations = Donation.objects.filter(donor=request.user, status='available').count()
    reserved_donations = Donation.objects.filter(donor=request.user, status='reserved').count()
    delivered_donations = Donation.objects.filter(donor=request.user, status='delivered').count()
    
    # Get recent donations (last 5)
    recent_donations = Donation.objects.filter(donor=request.user).order_by('-donated_at')[:5]
    
    # Expiring donations warning
    user_expiring = Donation.objects.expiring_within(days=10).filter(donor=request.user)
    critical_donations = user_expiring.filter(expiry_date__lte=date.today() + timedelta(days=3))
    
    context.update({
        'total_donations': total_donations,
        'available_donations': available_donations,
        'reserved_donations': reserved_donations,
        'delivered_donations': delivered_donations,
        'recent_donations': recent_donations,
        'user_expiring_donations': user_expiring,
        'user_critical_donations': critical_donations,
    })
    
    # ===== RECIPIENT STATISTICS =====
    user_requests = MedicineRequest.objects.filter(recipient=request.user)
    
    context.update({
        'total_requests': user_requests.count(),
        'pending_requests': user_requests.filter(status=MedicineRequest.Status.PENDING).count(),
        'matched_requests': user_requests.filter(status=MedicineRequest.Status.MATCHED).count(),
        'available_medicines': Donation.objects.filter(
            status=Donation.Status.AVAILABLE,
            approval_status=Donation.ApprovalStatus.APPROVED
        ).count(),
        'recent_requests': user_requests.order_by('-created_at')[:5],
    })
    
    # Admin features (if staff)
    if request.user.is_staff:
        all_expiring = Donation.objects.expiring_within(days=14)
        
        context['critical_donations'] = all_expiring.filter(expiry_date__lte=date.today() + timedelta(days=1))
        context['high_priority_donations'] = all_expiring.filter(
            expiry_date__gt=date.today() + timedelta(days=1),
            expiry_date__lte=date.today() + timedelta(days=3)
        )
        context['medium_priority_donations'] = all_expiring.filter(
            expiry_date__gt=date.today() + timedelta(days=3),
            expiry_date__lte=date.today() + timedelta(days=7)
        )
        context['low_priority_donations'] = all_expiring.filter(
            expiry_date__gt=date.today() + timedelta(days=7)
        )
        
        context['total_expiring_count'] = all_expiring.count()
        context['recent_alerts'] = ExpiryAlert.objects.filter(
            alert_sent_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('donation')[:10]
    
    # Redirect to role-specific dashboard instead of unified dashboard
    try:
        # Redirect admins to admin dashboard
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        
        if request.user.is_donor:
            return redirect('dashboard:donor_dashboard')
        elif request.user.is_recipient:
            return redirect('dashboard:recipient_dashboard')
        else:
            return redirect('select_role')
    except Exception as e:
        logger.error(f"Error determining dashboard redirect: {str(e)}")
        return redirect('select_role')


@login_required
def donor_dashboard(request):
    """Professional Donor Dashboard - View and manage medicine donations"""
    # Ensure user is a donor
    try:
        if not request.user.is_donor:
            return redirect('dashboard:recipient_dashboard' if request.user.is_recipient else 'select_role')
    except Exception as e:
        logger.error(f"Error checking user role in donor_dashboard: {str(e)}")
        return redirect('select_role')
    
    context = {}
    
    # Donor statistics
    total_donations = Donation.objects.filter(donor=request.user).count()
    
    # Separate pending and approved donations
    pending_approval_donations = Donation.objects.filter(
        donor=request.user,
        approval_status=Donation.ApprovalStatus.PENDING
    ).order_by('-donated_at')
    
    reserved_donations = Donation.objects.filter(
        donor=request.user,
        status=Donation.Status.RESERVED,
        approval_status=Donation.ApprovalStatus.APPROVED
    ).count()
    
    # Count settled requests (claimed medicines) instead of donation status
    delivered_donations = MedicineRequest.objects.filter(
        matched_donation__donor=request.user,
        status=MedicineRequest.Status.CLAIMED,
        approval_status=MedicineRequest.ApprovalStatus.APPROVED
    ).count()
    
    # Recent approved donations only
    recent_donations = Donation.objects.filter(
        donor=request.user,
        approval_status=Donation.ApprovalStatus.APPROVED
    ).order_by('-donated_at')[:10]
    
    # Expiring donations warning
    user_expiring = Donation.objects.expiring_within(days=10).filter(donor=request.user)
    critical_donations = user_expiring.filter(expiry_date__lte=date.today() + timedelta(days=3))
    
    # Pending requests (matched but not yet claimed) - only show APPROVED requests
    pending_requests = MedicineRequest.objects.filter(
        matched_donation__donor=request.user,
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,  # Only show approved requests
        status__in=[MedicineRequest.Status.MATCHED, MedicineRequest.Status.FULFILLED]
    ).order_by('-created_at')[:10]
    
    # Settled requests (claimed by recipient) - only show APPROVED requests
    settled_requests = MedicineRequest.objects.filter(
        matched_donation__donor=request.user,
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,  # Only show approved requests
        status=MedicineRequest.Status.CLAIMED
    ).order_by('-created_at')[:10]
    
    # All available medicines for browsing (only show APPROVED donations with quantity > 0)
    all_available_medicines = Donation.objects.filter(
        status=Donation.Status.AVAILABLE,
        approval_status=Donation.ApprovalStatus.APPROVED,  # Only show approved donations
        quantity__gt=0
    ).order_by('-donated_at')[:50]  # Limit to 50 most recent
    
    context.update({
        'total_donations': total_donations,
        'pending_approval_donations': pending_approval_donations,
        'pending_approval_count': pending_approval_donations.count(),
        'reserved_donations': reserved_donations,
        'delivered_donations': delivered_donations,
        'recent_donations': recent_donations,
        'user_expiring_donations': user_expiring,
        'user_critical_donations': critical_donations,
        'pending_requests': pending_requests,
        'settled_requests': settled_requests,
        'all_available_medicines': all_available_medicines,
    })
    
    return render(request, "dashboard/donor_dashboard.html", context)


@login_required
def recipient_dashboard(request):
    """Professional Recipient Dashboard - View and request medicines"""
    # Ensure user is a recipient
    try:
        if not request.user.is_recipient:
            return redirect('dashboard:donor_dashboard' if request.user.is_donor else 'select_role')
    except Exception as e:
        logger.error(f"Error checking user role in recipient_dashboard: {str(e)}")
        return redirect('select_role')
    
    context = {}
    
    # Recipient statistics
    user_requests = MedicineRequest.objects.filter(recipient=request.user)
    
    total_requests = user_requests.count()
    
    # Separate pending approval from approved pending/matched requests
    pending_approval_requests = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.PENDING
    ).order_by('-created_at')
    
    # Pending counter should include only APPROVED requests that are PENDING or MATCHED
    pending_requests = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status__in=[MedicineRequest.Status.PENDING, MedicineRequest.Status.MATCHED]
    ).count()
    
    fulfilled_requests = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status=MedicineRequest.Status.FULFILLED
    ).count()
    
    claimed_count = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status=MedicineRequest.Status.CLAIMED
    ).count()
    
    # Recently donated medicines (most recent first, only show APPROVED available ones with quantity > 0)
    available_medicines = Donation.objects.filter(
        status=Donation.Status.AVAILABLE,
        approval_status=Donation.ApprovalStatus.APPROVED,  # Only show approved donations
        quantity__gt=0
    ).order_by('-donated_at')[:3]
    available_medicines_count = Donation.objects.filter(
        status=Donation.Status.AVAILABLE,
        approval_status=Donation.ApprovalStatus.APPROVED,  # Only show approved donations
        quantity__gt=0
    ).count()
    
    # All available medicines for browse modal (only APPROVED)
    all_available_medicines = Donation.objects.filter(
        status=Donation.Status.AVAILABLE,
        approval_status=Donation.ApprovalStatus.APPROVED,  # Only show approved donations
        quantity__gt=0
    ).prefetch_related('matched_requests__recipient').order_by('-donated_at')[:50]
    
    # Recent requests (only approved ones that are pending, matched, or fulfilled)
    recent_requests = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status__in=[MedicineRequest.Status.PENDING, MedicineRequest.Status.MATCHED, MedicineRequest.Status.FULFILLED]
    ).order_by('-created_at')[:10]
    
    # Medicines ready to claim (approved by admin, not yet claimed)
    ready_to_claim = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status__in=[MedicineRequest.Status.MATCHED, MedicineRequest.Status.FULFILLED]
    ).select_related('matched_donation', 'matched_donation__donor').order_by('-reviewed_at')
    
    # Claimed medicines (only approved ones)
    claimed_medicines = user_requests.filter(
        approval_status=MedicineRequest.ApprovalStatus.APPROVED,
        status=MedicineRequest.Status.CLAIMED
    ).order_by('-created_at')[:10]
    
    context.update({
        'total_requests': total_requests,
        'pending_approval_requests': pending_approval_requests,
        'pending_approval_count': pending_approval_requests.count(),
        'pending_requests': pending_requests,
        'fulfilled_requests': fulfilled_requests,
        'claimed_count': claimed_count,
        'available_medicines': available_medicines,
        'all_available_medicines': all_available_medicines,
        'available_medicines_count': available_medicines_count,
        'recent_requests': recent_requests,
        'ready_to_claim': ready_to_claim,
        'ready_to_claim_count': ready_to_claim.count(),
        'claimed_medicines': claimed_medicines,
    })
    
    return render(request, "dashboard/recipient_dashboard.html", context)
