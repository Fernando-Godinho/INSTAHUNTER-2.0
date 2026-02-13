// Main JavaScript for InstaHunter 2.0

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[href*="delete"]');
    deleteButtons.forEach(button => {
        if (!button.closest('form')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Tem certeza que deseja deletar este item?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Add loading state to forms on submit
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';
            }
        });
    });
});

// Function to check instance status via AJAX
function checkInstanceStatus(instanceId) {
    const statusElement = document.querySelector(`#status-${instanceId}`);
    if (!statusElement) return;

    // Add loading state
    statusElement.classList.add('loading');

    fetch(`/instances/${instanceId}/status/`)
        .then(response => response.json())
        .then(data => {
            console.log('Status data:', data);
            
            // Update UI based on status
            const instance = data.instance;
            if (instance && instance.state) {
                updateStatusBadge(statusElement, instance.state);
            }
            
            statusElement.classList.remove('loading');
        })
        .catch(error => {
            console.error('Error checking status:', error);
            statusElement.classList.remove('loading');
            showToast('Erro ao verificar status', 'danger');
        });
}

// Update status badge
function updateStatusBadge(element, state) {
    const badges = {
        'open': '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Conectada</span>',
        'close': '<span class="badge bg-warning"><i class="bi bi-x-circle"></i> Desconectada</span>',
        'connecting': '<span class="badge bg-info"><i class="bi bi-arrow-repeat"></i> Conectando...</span>'
    };
    
    element.innerHTML = badges[state] || badges['close'];
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.querySelector('.toast-container').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Copy to clipboard function
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="bi bi-check"></i> Copiado!';
        buttonElement.classList.remove('btn-outline-primary');
        buttonElement.classList.add('btn-success');
        
        setTimeout(function() {
            buttonElement.innerHTML = originalText;
            buttonElement.classList.remove('btn-success');
            buttonElement.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(function(err) {
        console.error('Erro ao copiar:', err);
        showToast('Erro ao copiar para área de transferência', 'danger');
    });
}

// Format phone number
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 13) {
        value = value.substring(0, 13);
    }
    
    input.value = value;
}

// Validate form before submit
function validateInstanceForm(form) {
    const instanceName = form.querySelector('[name="instance_name"]');
    
    if (!instanceName.value.trim()) {
        showToast('Por favor, preencha o nome da instância', 'warning');
        instanceName.focus();
        return false;
    }
    
    // Check if instance name has special characters
    const namePattern = /^[a-zA-Z0-9_-]+$/;
    if (!namePattern.test(instanceName.value)) {
        showToast('O nome da instância deve conter apenas letras, números, underscore e hífen', 'warning');
        instanceName.focus();
        return false;
    }
    
    return true;
}
