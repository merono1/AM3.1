/**
 * partidas_contraibles_desc.js - Solución para contraer/expandir las descripciones de las partidas
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
  console.log('Iniciando solución para descripciones contraíbles de partidas');
  
  // Definimos estilos CSS directamente en el documento
  const style = document.createElement('style');
  style.textContent = `
    /* Estilo para las celdas de descripción contraída */
    .descripcion-celda {
      position: relative;
      overflow: hidden;
      transition: max-height 0.25s ease-in-out;
    }
    
    .descripcion-contraida {
      max-height: 80px; /* Altura máxima cuando está contraída */
    }
    
    .descripcion-expandida {
      max-height: 1000px; /* Altura suficiente cuando está expandida */
      transition: max-height 0.4s ease-in-out;
    }
    
    /* Añadir un desvanecimiento gradual al texto contraído */
    .descripcion-contraida::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 30px;
      background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,1));
      pointer-events: none;
    }
    
    /* Botón para expandir/contraer */
    .btn-toggle-descripcion {
      position: absolute;
      right: 10px;
      bottom: 5px;
      padding: 2px 5px;
      font-size: 10px;
      background-color: #f8f9fa;
      border: 1px solid #ddd;
      border-radius: 3px;
      cursor: pointer;
      z-index: 10;
      transition: all 0.2s;
      color: #0d6efd;
      box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .btn-toggle-descripcion:hover {
      background-color: #e9ecef;
      color: #0a58ca;
      box-shadow: 0 2px 3px rgba(0,0,0,0.15);
    }
    
    /* Para mantener los botones de acción siempre visibles */
    .acciones-partida {
      z-index: 20;
      position: relative;
    }
    
    /* Estilo para ocultar los detalles de las partidas inicialmente */
    .partida-fila-2 {
      display: none;
    }
    
    /* Estilo para la fila de partida cuando está activa */
    .partida-fila-1.activa {
      background-color: #eef2ff !important;
    }
    
    /* Añadir indicador de expansión para los campos numéricos */
    .partida-fila-1 td:first-child {
      position: relative;
    }
    
    .partida-fila-1 td:first-child:before {
      content: '▶';
      position: absolute;
      left: -5px;
      color: #6b7280;
      font-size: 10px;
      top: 50%;
      transform: translateY(-50%);
      transition: transform 0.2s;
    }
    
    .partida-fila-1.activa td:first-child:before {
      transform: translateY(-50%) rotate(90deg);
      color: #4f46e5;
    }
    
    /* Añadir cursor de puntero a las filas de partida */
    .partida-fila-1 {
      cursor: pointer;
    }
    
    /* Mejorar la apariencia de las filas activas */
    .partida-fila-1.activa + .partida-fila-2 {
      background-color: #f8faff;
    }
  `;
  document.head.appendChild(style);
  
  // Identificar todas las celdas de descripción
  const celdasDescripcion = document.querySelectorAll('.descripcion-celda');
  
  // Procesar cada celda de descripción
  celdasDescripcion.forEach(celda => {
    // Contraer inicialmente todas las descripciones
    celda.classList.add('descripcion-contraida');
    
    // Crear botón para expandir/contraer
    const btnToggle = document.createElement('button');
    btnToggle.className = 'btn-toggle-descripcion';
    btnToggle.textContent = 'Ver más';
    btnToggle.type = 'button';
    
    // Añadir el botón a la celda
    celda.appendChild(btnToggle);
    
    // Manejar evento de clic para expandir/contraer
    btnToggle.addEventListener('click', function(event) {
      // Prevenir que el clic se propague a la fila
      event.stopPropagation();
      
      const estaContraida = celda.classList.contains('descripcion-contraida');
      
      if (estaContraida) {
        // Expandir
        celda.classList.remove('descripcion-contraida');
        celda.classList.add('descripcion-expandida');
        btnToggle.textContent = 'Ver menos';
      } else {
        // Contraer
        celda.classList.remove('descripcion-expandida');
        celda.classList.add('descripcion-contraida');
        btnToggle.textContent = 'Ver más';
      }
    });
  });
  
  // Mantener expandida la descripción cuando se inicia la edición
  document.querySelectorAll('.editar-partida-btn').forEach(boton => {
    boton.addEventListener('click', function() {
      // Obtener el ID de la partida del atributo onclick
      const onclick = boton.getAttribute('onclick') || '';
      const match = onclick.match(/iniciarEdicionPartida\s*\(\s*['"]([^'"]+)['"]/);
      if (!match || !match[1]) return;
      
      const partidaId = match[1];
      
      // Encontrar la fila y la celda de descripción correspondiente
      const filaPartida = document.querySelector(`.partida-fila-1[data-partida-id="${partidaId}"]`);
      if (!filaPartida) return;
      
      const celdaDescripcion = filaPartida.querySelector('.descripcion-celda');
      if (!celdaDescripcion) return;
      
      // Expandir la descripción
      celdaDescripcion.classList.remove('descripcion-contraida');
      celdaDescripcion.classList.add('descripcion-expandida');
      
      // Actualizar el texto del botón
      const btnToggle = celdaDescripcion.querySelector('.btn-toggle-descripcion');
      if (btnToggle) {
        btnToggle.textContent = 'Ver menos';
      }
    });
  });
  
  // ================================================================
  // Implementar la funcionalidad para expandir/contraer la fila de datos numéricos
  // ================================================================
  
  // Identificar todas las filas de partidas
  const filasPartida = document.querySelectorAll('.partida-fila-1');
  
  // Añadir evento de clic a cada fila de partida para expandir/contraer los datos numéricos
  filasPartida.forEach(fila => {
    fila.addEventListener('click', function(event) {
      // No activar si se hizo clic en un botón o en el botón de ver más/menos
      if (event.target.closest('button') || event.target.closest('.btn-toggle-descripcion')) {
        return;
      }
      
      // Obtener el ID de la partida
      const partidaId = fila.dataset.partidaId;
      if (!partidaId) return;
      
      // Encontrar la fila de datos correspondiente
      const filaDatos = document.querySelector(`.partida-fila-2[data-partida-id="${partidaId}"]`);
      if (!filaDatos) return;
      
      // Determinar si estamos activando o desactivando
      const estaActiva = fila.classList.contains('activa');
      
      // Si estamos activando esta fila, primero desactivar todas las demás
      if (!estaActiva) {
        // Ocultar todas las filas de datos y quitar la clase activa
        document.querySelectorAll('.partida-fila-1').forEach(f => f.classList.remove('activa'));
        document.querySelectorAll('.partida-fila-2').forEach(f => f.style.display = 'none');
      }
      
      // Alternar estado
      if (estaActiva) {
        // Desactivar
        fila.classList.remove('activa');
        filaDatos.style.display = 'none';
      } else {
        // Activar
        fila.classList.add('activa');
        filaDatos.style.display = 'table-row';
      }
    });
  });
  
  // También adaptar el comportamiento de los botones de edición
  document.querySelectorAll('.editar-partida-btn').forEach(boton => {
    boton.addEventListener('click', function() {
      // Obtener el ID de la partida del atributo onclick
      const onclick = boton.getAttribute('onclick') || '';
      const match = onclick.match(/iniciarEdicionPartida\s*\(\s*['"]([^'"]+)['"]/);
      if (!match || !match[1]) return;
      
      const partidaId = match[1];
      
      // Encontrar las filas correspondientes
      const filaPartida = document.querySelector(`.partida-fila-1[data-partida-id="${partidaId}"]`);
      const filaDatos = document.querySelector(`.partida-fila-2[data-partida-id="${partidaId}"]`);
      
      if (filaPartida && filaDatos) {
        // Ocultar todas las filas de datos primero
        document.querySelectorAll('.partida-fila-1').forEach(f => f.classList.remove('activa'));
        document.querySelectorAll('.partida-fila-2').forEach(f => f.style.display = 'none');
        
        // Mostrar solo esta fila
        filaPartida.classList.add('activa');
        filaDatos.style.display = 'table-row';
      }
    });
  });
  
  console.log('Solución de descripciones y datos contraíbles aplicada');
});
