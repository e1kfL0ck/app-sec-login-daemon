/**
 * Main JavaScript file for the login daemon
 */

// Log when the page is loaded
console.log('Login daemon application loaded');

// Add event listener for form validation
document.addEventListener('DOMContentLoaded', function() {
    // Handle flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-messages > div');
    flashMessages.forEach(function(message) {
        // Auto-dismiss success messages after 5 seconds
        if (message.classList.contains('flash-success')) {
            setTimeout(function() {
                message.style.transition = 'opacity 0.5s';
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 500);
            }, 5000);
        }
    });
});
