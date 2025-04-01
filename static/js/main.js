// main.js - Main JavaScript file for Windows Auth application

document.addEventListener('DOMContentLoaded', function() {
    // Flash message handling
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Add close button to flash messages
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'close-button';
        closeButton.onclick = function() {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        };
        message.appendChild(closeButton);

        // Auto-hide flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Create or update error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = `${field.name} is required`;
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                event.preventDefault();
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.hasAttribute('required') && this.value.trim()) {
                    this.classList.remove('error');
                    const errorMsg = this.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
        });
    });

    // Add loading indicator for form submissions
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (this.checkValidity()) {
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton) {
                    const originalText = submitButton.innerHTML;
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="spinner"></span> Processing...';
                    
                    // Reset button after 10 seconds (failsafe)
                    setTimeout(() => {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }, 10000);
                }
            }
        });
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;

            this.addEventListener('mouseleave', () => tooltip.remove());
        });
    });
});

// Helper function to show loading state
function showLoading(element, message = 'Loading...') {
    element.disabled = true;
    element.dataset.originalText = element.innerHTML;
    element.innerHTML = `<span class="spinner"></span> ${message}`;
}

// Helper function to hide loading state
function hideLoading(element) {
    element.disabled = false;
    element.innerHTML = element.dataset.originalText;
    delete element.dataset.originalText;
}

// Add corresponding CSS to support the JavaScript functionality
const style = document.createElement('style');
style.textContent = `
    .flash-message {
        position: relative;
        padding: 1rem 2rem 1rem 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        opacity: 1;
        transition: opacity 0.3s ease-in-out;
    }

    .close-button {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0 5px;
        color: inherit;
    }

    .error {
        border-color: #dc3545 !important;
    }

    .error-message {
        color: #dc3545;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }

    .spinner {
        display: inline-block;
        width: 1em;
        height: 1em;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 0.5rem;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .tooltip {
        position: absolute;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 0.875rem;
        pointer-events: none;
        z-index: 1000;
    }
`;
document.head.appendChild(style);