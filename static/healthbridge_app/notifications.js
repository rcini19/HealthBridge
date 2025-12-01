// Notification Bell System JavaScript

// Notification Elements
const notificationBell = document.getElementById('notificationBell');
const notificationDropdown = document.getElementById('notificationDropdown');
const notificationBadge = document.getElementById('notificationBadge');
const notificationList = document.getElementById('notificationList');
const markAllReadBtn = document.getElementById('markAllReadBtn');

// Toggle dropdown
notificationBell.addEventListener('click', (e) => {
    e.stopPropagation();
    const isShowing = notificationDropdown.style.display === 'block';
    
    if (isShowing) {
        notificationDropdown.style.display = 'none';
        notificationDropdown.classList.remove('show');
    } else {
        notificationDropdown.style.display = 'block';
        notificationDropdown.classList.add('show');
        loadNotifications();
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!notificationDropdown.contains(e.target) && !notificationBell.contains(e.target)) {
        notificationDropdown.style.display = 'none';
        notificationDropdown.classList.remove('show');
    }
});

// Get CSRF token
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

const csrftoken = getCookie('csrftoken');

// Fetch unread count
async function updateUnreadCount() {
    try {
        const response = await fetch('/notifications/api/unread-count/');
        const data = await response.json();
        
        if (data.success && data.count > 0) {
            notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
            notificationBadge.style.display = 'flex';
            markAllReadBtn.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
            markAllReadBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching unread count:', error);
    }
}

// Load notifications
async function loadNotifications() {
    try {
        const response = await fetch('/notifications/api/');
        const data = await response.json();
        
        if (data.success && data.notifications.length > 0) {
            renderNotifications(data.notifications);
        } else {
            notificationList.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>No notifications yet</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        notificationList.innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load notifications</p>
            </div>
        `;
    }
}

// Render notifications
function renderNotifications(notifications) {
    const notificationsHTML = notifications.map(notif => {
        const unreadClass = notif.is_read ? '' : 'unread';

        // Determine icon and style class based on notification type keywords
        let iconClass = 'info';
        let iconHTML = '<i class="fas fa-bell" aria-hidden="true"></i>';

        // Support both server keys: `type` and `notification_type`
        const t = ((notif.type || notif.notification_type) || '').toUpperCase();
        if (t.includes('APPROVED')) {
            iconClass = 'approved';
            iconHTML = '<i class="fas fa-check" aria-hidden="true"></i>';
        } else if (t.includes('RECEIVED') || t.includes('REQUEST')) {
            iconClass = 'info';
            iconHTML = '<i class="fas fa-inbox" aria-hidden="true"></i>';
        } else if (t.includes('REJECT') || t.includes('REJECTION')) {
            iconClass = 'rejected';
            iconHTML = '<i class="fas fa-times" aria-hidden="true"></i>';
        } else if (t.includes('DONATION')) {
            iconClass = 'approved';
            iconHTML = '<i class="fas fa-hand-holding-heart" aria-hidden="true"></i>';
        }

        return `
            <div class="notification-item ${unreadClass}" data-id="${notif.id}" onclick="markAsRead(${notif.id})">
                <div class="notification-content">
                    <div class="notification-icon ${iconClass}">
                        ${iconHTML}
                    </div>
                    <div class="notification-text">
                        <div class="notification-title">${notif.title}</div>
                        <div class="notification-message">${notif.message}</div>
                        <div class="notification-time">${notif.time_ago}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    notificationList.innerHTML = notificationsHTML;
}

// Mark notification as read
async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/notifications/api/${notificationId}/read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update UI
            const notifElement = document.querySelector(`[data-id="${notificationId}"]`);
            if (notifElement) {
                notifElement.classList.remove('unread');
            }
            
            // Update badge count
            updateUnreadCount();
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Mark all as read
markAllReadBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    
    try {
        const response = await fetch('/notifications/api/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update all notification items
            document.querySelectorAll('.notification-item').forEach(item => {
                item.classList.remove('unread');
            });
            
            // Update badge
            updateUnreadCount();
            markAllReadBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
});

// Update unread count on page load and every 30 seconds
updateUnreadCount();
setInterval(updateUnreadCount, 30000);
