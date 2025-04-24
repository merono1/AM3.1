/**
 * partidas_contraibles_solucion.js - Versión modificada para mantener filas de datos visibles
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
  console.log('Iniciando solución modificada para partidas');
  
  // Definimos estilos CSS directamente en el documento
  const style = document.createElement('style');
  style.textContent = `
    /* Mostrar siempre los detalles de las partidas */
    .partida-fila-2 {
      display: table-row !important;
    }
    
    /* Estilos para la tabla de datos de partida */
    .tabla-datos-partida {
      background-color: #f8f9fa;
      margin-bottom: 0;
      padding: 4px;
      border-radius: 4px;
      font-size: 0.85rem;
    }
  `;
  document.head.appendChild(style);
  
  console.log('Solución de partidas aplicada - Filas de datos siempre visibles');
});
