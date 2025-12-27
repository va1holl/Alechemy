// Main JavaScript file for Alechemy

// Get CSRF token from cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
  // Set active nav item for mobile
  const currentUrl = window.location.pathname;
  document.querySelectorAll('.mobile-nav-item').forEach(item => {
    if (item.getAttribute('href') === currentUrl) {
      item.classList.add('active');
    }
  });
});

// Utility function to show loading state
function showLoading(element, text = 'Загрузка...') {
  if (element) {
    const originalText = element.textContent;
    element.disabled = true;
    element.innerHTML = `<span class="loading"></span> ${text}`;
    element.dataset.originalText = originalText;
  }
}

// Utility function to hide loading state
function hideLoading(element) {
  if (element && element.dataset.originalText) {
    element.textContent = element.dataset.originalText;
    element.disabled = false;
  }
}

// Confirm deletion
function confirmDelete(message = 'Ви впевнені?') {
  return confirm(message);
}

// Format date
function formatDate(dateString) {
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString('ru-RU', options);
}

// Toast notification
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#ef5350' : '#667eea'};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10000;
    animation: slideIn 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Export for use in templates
window.alechemy = {
  getCookie,
  showLoading,
  hideLoading,
  confirmDelete,
  formatDate,
  showToast
};
