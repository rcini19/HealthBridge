// Admin Dashboard JavaScript

// Get today's date for the date picker
const today = new Date().toISOString().split('T')[0];

function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

function openGuidelinesModal() {
    console.log('Opening guidelines modal...');
    const modal = document.getElementById('guidelinesModal');
    console.log('Modal element:', modal);
    if (modal) {
        showModal('guidelinesModal');
    } else {
        console.error('Guidelines modal not found!');
    }
}

function approveDonation(donationId) {
    if (confirm('Are you sure you want to approve this donation?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin-dashboard/approve-donation/${donationId}/`;
        
        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = getCookie('csrftoken');
        form.appendChild(csrf);
        
        document.body.appendChild(form);
        form.submit();
    }
}

function showRejectDonationModal(donationId, name) {
    const form = document.getElementById('rejectDonationForm');
    form.action = `/admin-dashboard/reject-donation/${donationId}/`;
    showModal('rejectDonationModal');
}

function showApproveRequestModal(requestId, name) {
    const form = document.getElementById('approveRequestForm');
    form.action = `/admin-dashboard/approve-request/${requestId}/`;
    showModal('approveRequestModal');
}

function showRejectRequestModal(requestId, name) {
    const form = document.getElementById('rejectRequestForm');
    form.action = `/admin-dashboard/reject-request/${requestId}/`;
    showModal('rejectRequestModal');
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// View donation details
async function viewDonationDetails(donationId) {
    showModal('viewDonationModal');
    const content = document.getElementById('donationDetailsContent');
    content.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    
    try {
        const response = await fetch(`/admin-dashboard/api/donation/${donationId}/`);
        const data = await response.json();
        
        const donation = data.donation;
        const donor = data.donor;
        
        content.innerHTML = `
            <div class="details-grid">
                <div class="details-section">
                    <h4><i class="fas fa-pills"></i> Donation Information</h4>
                    <div class="detail-item">
                        <strong>Medicine Name:</strong>
                        <span>${donation.name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Quantity:</strong>
                        <span>${donation.quantity} units</span>
                    </div>
                    <div class="detail-item">
                        <strong>Expiry Date:</strong>
                        <span>${donation.expiry_date} <em>(${donation.days_until_expiry} days)</em></span>
                    </div>
                    <div class="detail-item">
                        <strong>Tracking Code:</strong>
                        <span class="tracking-code">${donation.tracking_code}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Status:</strong>
                        <span class="badge">${donation.status}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Approval Status:</strong>
                        <span class="badge">${donation.approval_status}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Donated At:</strong>
                        <span>${donation.donated_at}</span>
                    </div>
                    <div class="detail-item full-width">
                        <strong>Notes:</strong>
                        <p>${donation.notes}</p>
                    </div>
                    ${donation.image_url ? `
                    <div class="detail-item full-width">
                        <strong>Medicine Image:</strong>
                        <div class="medicine-image-container">
                            <img src="${donation.image_url}" alt="${donation.name}" class="medicine-image">
                        </div>
                    </div>
                    ` : '<div class="detail-item full-width"><em>No image provided</em></div>'}
                </div>
                
                <div class="details-section">
                    <h4><i class="fas fa-user"></i> Donor Profile</h4>
                    <div class="detail-item">
                        <strong>Full Name:</strong>
                        <span>${donor.full_name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Username:</strong>
                        <span>@${donor.username}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Email:</strong>
                        <span>${donor.email}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Phone:</strong>
                        <span>${donor.phone}</span>
                    </div>
                    <div class="detail-item">
                        <strong>User Type:</strong>
                        <span class="badge">${donor.user_type}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Member Since:</strong>
                        <span>${donor.date_joined}</span>
                    </div>
                    <div class="detail-item full-width">
                        <strong>Address:</strong>
                        <p>${donor.address}</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="error">Failed to load details. Please try again.</div>`;
        console.error('Error fetching donation details:', error);
    }
}

// View request details
async function viewRequestDetails(requestId) {
    showModal('viewRequestModal');
    const content = document.getElementById('requestDetailsContent');
    content.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    
    try {
        const response = await fetch(`/admin-dashboard/api/request/${requestId}/`);
        const data = await response.json();
        
        const request = data.request;
        const recipient = data.recipient;
        const donation = data.matched_donation;
        
        content.innerHTML = `
            <div class="details-grid">
                <div class="details-section">
                    <h4><i class="fas fa-hand-holding-medical"></i> Request Information</h4>
                    <div class="detail-item">
                        <strong>Medicine Name:</strong>
                        <span>${request.medicine_name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Quantity:</strong>
                        <span>${request.quantity} units</span>
                    </div>
                    <div class="detail-item">
                        <strong>Urgency:</strong>
                        <span class="badge ${request.urgency_class}">${request.urgency}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Tracking Code:</strong>
                        <span class="tracking-code">${request.tracking_code}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Status:</strong>
                        <span class="badge">${request.status}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Approval Status:</strong>
                        <span class="badge">${request.approval_status}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Created At:</strong>
                        <span>${request.created_at} <em>(${request.days_since_request} days ago)</em></span>
                    </div>
                    <div class="detail-item">
                        <strong>Claim Ready Date:</strong>
                        <span>${request.claim_ready_date}</span>
                    </div>
                    <div class="detail-item full-width">
                        <strong>Reason:</strong>
                        <p>${request.reason}</p>
                    </div>
                    <div class="detail-item full-width">
                        <strong>Notes:</strong>
                        <p>${request.notes}</p>
                    </div>
                </div>
                
                <div class="details-section">
                    <h4><i class="fas fa-user"></i> Recipient Profile</h4>
                    <div class="detail-item">
                        <strong>Full Name:</strong>
                        <span>${recipient.full_name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Username:</strong>
                        <span>@${recipient.username}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Email:</strong>
                        <span>${recipient.email}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Phone:</strong>
                        <span>${recipient.phone}</span>
                    </div>
                    <div class="detail-item">
                        <strong>User Type:</strong>
                        <span class="badge">${recipient.user_type}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Member Since:</strong>
                        <span>${recipient.date_joined}</span>
                    </div>
                    <div class="detail-item full-width">
                        <strong>Address:</strong>
                        <p>${recipient.address}</p>
                    </div>
                </div>
                
                ${donation ? `
                <div class="details-section full-width">
                    <h4><i class="fas fa-link"></i> Matched Donation</h4>
                    <div class="detail-item">
                        <strong>Medicine:</strong>
                        <span>${donation.name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Quantity Available:</strong>
                        <span>${donation.quantity} units</span>
                    </div>
                    <div class="detail-item">
                        <strong>Tracking Code:</strong>
                        <span class="tracking-code">${donation.tracking_code}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Donor:</strong>
                        <span>${donation.donor_name}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Donor Email:</strong>
                        <span>${donation.donor_email}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Donor Phone:</strong>
                        <span>${donation.donor_phone}</span>
                    </div>
                    ${donation.image_url ? `
                    <div class="detail-item full-width">
                        <strong>Donation Image:</strong>
                        <div class="medicine-image-container">
                            <img src="${donation.image_url}" alt="${donation.name}" class="medicine-image">
                        </div>
                    </div>
                    ` : ''}
                </div>
                ` : '<div class="details-section full-width"><em>No matched donation yet</em></div>'}
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="error">Failed to load details. Please try again.</div>`;
        console.error('Error fetching request details:', error);
    }
}

// Show approved donations modal
function showApprovedDonationsModal() {
    showModal('approvedDonationsModal');
}

// Show approved requests modal
function showApprovedRequestsModal() {
    showModal('approvedRequestsModal');
}

// Close modals on background click
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });

    // Auto-hide messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.animation = 'slideOut 0.3s forwards';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
});
