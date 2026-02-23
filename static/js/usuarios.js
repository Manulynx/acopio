/* =================================================================
   UEB Acopio Bayamo - JavaScript para Gestión de Usuarios
   ================================================================= */

// Función para alternar estado de usuario
function toggleUserStatus(userId, username) {
    if (confirm(`¿Estás seguro de cambiar el estado del usuario "${username}"?`)) {
        fetch(`/usuarios/${userId}/alternar-estado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito
                showMessage(data.message, 'success');
                // Recargar la página para mostrar cambios
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error al cambiar el estado del usuario', 'error');
        });
    }
}

// Función para mostrar mensajes de notificación
function showMessage(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insertar al inicio del contenedor
    const container = document.querySelector('.container-fluid') || document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

// Función para obtener el token CSRF
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

// Función para asegurar que existe el token CSRF
function ensureCSRFToken() {
    if (!document.querySelector('[name=csrfmiddlewaretoken]')) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrfToken;
            document.body.appendChild(input);
        }
    }
}

// Inicialización cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Asegurar token CSRF
    ensureCSRFToken();
    
    // Inicializar funcionalidades específicas según la página
    if (document.getElementById('usuarios-index')) {
        initUsuariosIndex();
    }
    
    if (document.getElementById('usuario-crear')) {
        initUsuarioCrear();
    }
    
    if (document.getElementById('usuario-editar')) {
        initUsuarioEditar();
    }
    
    if (document.getElementById('usuario-eliminar')) {
        initUsuarioEliminar();
    }
    
    if (document.getElementById('login-form')) {
        initLogin();
    }
});

// Inicialización para la página de lista de usuarios
function initUsuariosIndex() {
    // Ya está configurado con las funciones globales
    console.log('Lista de usuarios inicializada');
}

// Inicialización para crear usuario
function initUsuarioCrear() {
    // Enfocar el campo username al cargar
    const usernameField = document.getElementById('id_username');
    if (usernameField) {
        usernameField.focus();
    }
    
    // Generar sugerencia de username basado en nombre y apellido
    const firstNameField = document.getElementById('id_first_name');
    const lastNameField = document.getElementById('id_last_name');
    
    function generateUsername() {
        const firstName = firstNameField?.value.trim().toLowerCase() || '';
        const lastName = lastNameField?.value.trim().toLowerCase() || '';
        
        if (firstName && lastName && usernameField) {
            // Crear sugerencia: primera letra del nombre + apellido
            const suggestion = (firstName.charAt(0) + lastName).replace(/[^a-z0-9]/g, '');
            if (suggestion && !usernameField.value) {
                usernameField.placeholder = `Sugerencia: ${suggestion}`;
            }
        }
    }
    
    if (firstNameField && lastNameField) {
        firstNameField.addEventListener('blur', generateUsername);
        lastNameField.addEventListener('blur', generateUsername);
    }
}

// Inicialización para editar usuario
function initUsuarioEditar() {
    // Validación en tiempo real de contraseñas
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    
    function validatePasswords() {
        if (password1 && password2 && password1.value && password2.value) {
            if (password1.value !== password2.value) {
                password2.setCustomValidity('Las contraseñas no coinciden');
                password2.classList.add('is-invalid');
                password2.classList.remove('is-valid');
            } else {
                password2.setCustomValidity('');
                password2.classList.remove('is-invalid');
                password2.classList.add('is-valid');
            }
        } else if (password2) {
            password2.setCustomValidity('');
            password2.classList.remove('is-invalid', 'is-valid');
        }
    }
    
    if (password1 && password2) {
        password1.addEventListener('input', validatePasswords);
        password2.addEventListener('input', validatePasswords);
    }
    
    // Confirmación antes de enviar si hay cambios en contraseña
    const form = document.querySelector('form');
    if (form && password1 && password2) {
        form.addEventListener('submit', function(e) {
            if (password1.value || password2.value) {
                if (!confirm('¿Estás seguro de cambiar la contraseña de este usuario?')) {
                    e.preventDefault();
                }
            }
        });
    }
}

// Inicialización para eliminar usuario
function initUsuarioEliminar() {
    const confirmInput = document.getElementById('confirm_username');
    const deleteBtn = document.getElementById('delete-btn');
    const expectedUsername = deleteBtn?.getAttribute('data-username');
    
    // Validar entrada de confirmación
    if (confirmInput && deleteBtn && expectedUsername) {
        confirmInput.addEventListener('input', function() {
            if (this.value.trim() === expectedUsername) {
                deleteBtn.disabled = false;
                deleteBtn.classList.remove('btn-secondary');
                deleteBtn.classList.add('btn-danger');
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                deleteBtn.disabled = true;
                deleteBtn.classList.remove('btn-danger');
                deleteBtn.classList.add('btn-secondary');
                this.classList.remove('is-valid');
                if (this.value.trim() !== '') {
                    this.classList.add('is-invalid');
                }
            }
        });
        
        // Enfocar el campo de confirmación
        confirmInput.focus();
    }
    
    // Confirmación final antes de enviar
    const form = document.querySelector('form');
    if (form && expectedUsername) {
        form.addEventListener('submit', function(e) {
            if (!confirm(`¿ESTÁS COMPLETAMENTE SEGURO de eliminar al usuario "${expectedUsername}"?\n\nEsta acción NO SE PUEDE DESHACER.`)) {
                e.preventDefault();
            }
        });
    }
}

// Inicialización para login
function initLogin() {
    // Enfocar el campo usuario al cargar
    const usernameField = document.getElementById('id_username');
    if (usernameField) {
        usernameField.focus();
    }
    
    // Animar el formulario al cargar
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = '0';
        loginCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            loginCard.style.transition = 'all 0.6s ease';
            loginCard.style.opacity = '1';
            loginCard.style.transform = 'translateY(0)';
        }, 100);
    }
}