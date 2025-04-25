/**
 * Manejo de los botones de proveedores para hojas de trabajo
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configurar botones para mostrar proveedores adicionales
    document.querySelectorAll('.btn-proveedores-adicionales').forEach(function(btn) {
        if (btn.hasAttribute('data-partida-id')) {
            btn.addEventListener('click', function() {
                const partidaId = this.getAttribute('data-partida-id');
                // URL para gestionar los proveedores de una partida específica
                window.location.href = `/proveedores-partidas/gestionar/${partidaId}`;
            });
        }
    });

    // Función para mostrar estado de proveedores
    function actualizarEstadoProveedores() {
        // Buscar partidas con proveedores asignados
        document.querySelectorAll('.partida').forEach(function(partida) {
            const partidaId = partida.getAttribute('data-partida-id');
            if (!partidaId) return;
            
            // Verificar si tiene proveedores mediante una llamada API
            fetch(`/api/proveedores-partidas/por-partida/${partidaId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.proveedores && data.proveedores.length > 0) {
                        // Tiene proveedores, actualizar el botón para indicarlo
                        const btnProveedores = partida.querySelector('.btn-proveedores');
                        if (btnProveedores) {
                            btnProveedores.innerHTML = `Proveedores (${data.proveedores.length})`;
                            btnProveedores.classList.add('btn-success');
                            btnProveedores.classList.remove('btn-info');
                        }
                        
                        // Actualizar el botón de proveedores adicionales
                        const btnProveedoresAdicionales = partida.querySelector('.btn-proveedores-adicionales');
                        if (btnProveedoresAdicionales) {
                            btnProveedoresAdicionales.classList.add('btn-primary');
                            btnProveedoresAdicionales.classList.remove('btn-secondary');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error al verificar proveedores:', error);
                });
        });
    }
    
    // Actualizar estado inicial
    setTimeout(actualizarEstadoProveedores, 500);
});
