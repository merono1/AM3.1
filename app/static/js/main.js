/**
 * Archivo JavaScript principal para la aplicación AM3.1
 */

// Función para validar formularios antes de enviar
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    // Añadir aquí cualquier validación personalizada
    console.log('Validando formulario:', formId);

    // Si todo está correcto, permitir el envío del formulario
    return true;
}

// Inicializar selectores cuando se cargue la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página cargada, inicializando componentes...');
    
    // Activar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar select2 si está disponible
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%'
        });
    }
});
