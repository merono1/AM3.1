/**
 * editor_inline.js - Editor de texto enriquecido directamente en la vista
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Iniciando editor de texto en línea');
  
  // Agregar estilos necesarios
  const style = document.createElement('style');
  style.textContent = `
    /* Estilos para el editor inline */
    .descripcion-editable {
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      min-height: 100px;
      overflow: auto;
      background-color: #fff;
      transition: border-color 0.2s;
    }
    
    .descripcion-editable:focus {
      outline: none;
      border-color: #80bdff;
      box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    }
    
    /* Toolbar de edición */
    .editor-toolbar {
      display: flex;
      background-color: #f8f9fa;
      border: 1px solid #ddd;
      border-bottom: none;
      border-radius: 4px 4px 0 0;
      padding: 4px;
    }
    
    .editor-toolbar button {
      width: 30px;
      height: 30px;
      margin: 0 2px;
      background-color: transparent;
      border: 1px solid transparent;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }
    
    .editor-toolbar button:hover {
      background-color: #e9ecef;
      border-color: #ced4da;
    }
    
    .editor-toolbar button.active {
      background-color: #daeafe;
      border-color: #b9d6fb;
    }
    
    .editor-toolbar .editor-divider {
      width: 1px;
      height: 20px;
      background-color: #ced4da;
      margin: 0 5px;
      align-self: center;
    }
    
    /* Contenedor del editor */
    .editor-container {
      margin-bottom: 15px;
      display: none; /* Inicialmente oculto */
    }
    
    /* Capa transparente que bloquea clicks cuando no estamos editando */
    .descripcion-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: transparent;
      z-index: 10;
    }
    
    /* Clases para la celda en modo edición */
    .descripcion-celda.editando {
      position: relative;
      padding: 0 !important;
    }
    
    /* Botones de acción en la barra de edición */
    .editor-actions {
      margin-left: auto;
    }
    
    .editor-actions button {
      width: auto;
      padding: 0 8px;
      font-size: 12px;
      font-weight: normal;
    }
    
    .btn-save-edit {
      color: #fff;
      background-color: #28a745 !important;
      border-color: #28a745 !important;
    }
    
    .btn-save-edit:hover {
      background-color: #218838 !important;
      border-color: #1e7e34 !important;
    }
    
    .btn-cancel-edit {
      color: #fff;
      background-color: #dc3545 !important;
      border-color: #dc3545 !important;
    }
    
    .btn-cancel-edit:hover {
      background-color: #c82333 !important;
      border-color: #bd2130 !important;
    }
  `;
  document.head.appendChild(style);
  
  // Crear el toolbar del editor
  function crearToolbar(partidaId) {
    const toolbar = document.createElement('div');
    toolbar.className = 'editor-toolbar';
    
    // Botones de formato
    const btnBold = document.createElement('button');
    btnBold.type = 'button';
    btnBold.title = 'Negrita';
    btnBold.innerHTML = '<strong>B</strong>';
    btnBold.addEventListener('click', () => execCommand('bold'));
    
    const btnItalic = document.createElement('button');
    btnItalic.type = 'button';
    btnItalic.title = 'Cursiva';
    btnItalic.innerHTML = '<i>I</i>';
    btnItalic.addEventListener('click', () => execCommand('italic'));
    
    const btnUnderline = document.createElement('button');
    btnUnderline.type = 'button';
    btnUnderline.title = 'Subrayado';
    btnUnderline.innerHTML = '<u>U</u>';
    btnUnderline.addEventListener('click', () => execCommand('underline'));
    
    const btnStrike = document.createElement('button');
    btnStrike.type = 'button';
    btnStrike.title = 'Tachado';
    btnStrike.innerHTML = '<s>S</s>';
    btnStrike.addEventListener('click', () => execCommand('strikeThrough'));
    
    // Separador
    const divider1 = document.createElement('div');
    divider1.className = 'editor-divider';
    
    // Botones de listas
    const btnBulletList = document.createElement('button');
    btnBulletList.type = 'button';
    btnBulletList.title = 'Lista con viñetas';
    btnBulletList.innerHTML = '•';
    btnBulletList.addEventListener('click', () => execCommand('insertUnorderedList'));
    
    const btnNumberList = document.createElement('button');
    btnNumberList.type = 'button';
    btnNumberList.title = 'Lista numerada';
    btnNumberList.innerHTML = '1.';
    btnNumberList.addEventListener('click', () => execCommand('insertOrderedList'));
    
    // Separador
    const divider2 = document.createElement('div');
    divider2.className = 'editor-divider';
    
    // Botones de acción (guardar, cancelar)
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'editor-actions';
    
    const btnSave = document.createElement('button');
    btnSave.type = 'button';
    btnSave.className = 'btn-save-edit';
    btnSave.textContent = 'Guardar';
    btnSave.addEventListener('click', () => guardarCambios(partidaId));
    
    const btnCancel = document.createElement('button');
    btnCancel.type = 'button';
    btnCancel.className = 'btn-cancel-edit';
    btnCancel.textContent = 'Cancelar';
    btnCancel.addEventListener('click', () => cancelarEdicion(partidaId));
    
    actionsDiv.appendChild(btnSave);
    actionsDiv.appendChild(btnCancel);
    
    // Añadir todos los elementos al toolbar
    toolbar.appendChild(btnBold);
    toolbar.appendChild(btnItalic);
    toolbar.appendChild(btnUnderline);
    toolbar.appendChild(btnStrike);
    toolbar.appendChild(divider1);
    toolbar.appendChild(btnBulletList);
    toolbar.appendChild(btnNumberList);
    toolbar.appendChild(divider2);
    toolbar.appendChild(actionsDiv);
    
    return toolbar;
  }
  
  // Función para ejecutar comandos de edición
  function execCommand(command, value = null) {
    document.execCommand(command, false, value);
  }
  
  // Convertir todas las celdas de descripción para hacerlas editables con doble clic
  document.querySelectorAll('.descripcion-celda').forEach(celda => {
    // Obtener el ID de la partida
    const fila = celda.closest('.partida-fila-1');
    if (!fila) return;
    
    const partidaId = fila.dataset.partidaId;
    if (!partidaId) return;
    
    // Guardar el contenido original
    celda.dataset.originalContent = celda.innerHTML;
    
    // Añadir una capa transparente para manejar doble clic
    const overlay = document.createElement('div');
    overlay.className = 'descripcion-overlay';
    celda.style.position = 'relative';
    celda.appendChild(overlay);
    
    // Manejar doble clic para iniciar edición
    overlay.addEventListener('dblclick', () => iniciarEdicion(partidaId, celda));
    
    // También permitir iniciar la edición al hacer clic en el botón de editar
    document.querySelector(`.editar-partida-btn[onclick*="${partidaId}"]`)?.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      iniciarEdicion(partidaId, celda);
    });
  });
  
  // Función para iniciar la edición
  function iniciarEdicion(partidaId, celda) {
    console.log(`Iniciando edición de la partida ${partidaId}`);
    
    // Verificar si ya hay alguna celda en edición y cancelarla
    const celdaEditandoActual = document.querySelector('.descripcion-celda.editando');
    if (celdaEditandoActual) {
      const idPartidaActual = celdaEditandoActual.closest('.partida-fila-1')?.dataset.partidaId;
      if (idPartidaActual) {
        cancelarEdicion(idPartidaActual);
      }
    }
    
    // Remover overlay
    celda.querySelector('.descripcion-overlay')?.remove();
    
    // Marcar celda como en edición
    celda.classList.add('editando');
    
    // Guardar el contenido original antes de editar
    if (!celda.dataset.originalContent) {
      celda.dataset.originalContent = celda.innerHTML;
    }
    
    // Crear contenedor del editor
    const editorContainer = document.createElement('div');
    editorContainer.className = 'editor-container';
    editorContainer.id = `editor-container-${partidaId}`;
    
    // Crear el toolbar
    const toolbar = crearToolbar(partidaId);
    
    // Crear el área editable
    const editorArea = document.createElement('div');
    editorArea.className = 'descripcion-editable';
    editorArea.id = `editor-area-${partidaId}`;
    editorArea.contentEditable = true;
    editorArea.innerHTML = celda.dataset.originalContent;
    
    // Añadir elementos al contenedor
    editorContainer.appendChild(toolbar);
    editorContainer.appendChild(editorArea);
    
    // Limpiar contenido de la celda y añadir el editor
    celda.innerHTML = '';
    celda.appendChild(editorContainer);
    
    // Mostrar el editor
    editorContainer.style.display = 'block';
    
    // Enfocar el editor
    setTimeout(() => {
      editorArea.focus();
    }, 0);
  }
  
  // Función para guardar los cambios
  function guardarCambios(partidaId) {
    console.log(`Guardando cambios de la partida ${partidaId}`);
    
    const celda = document.querySelector(`.partida-fila-1[data-partida-id="${partidaId}"] .descripcion-celda`);
    if (!celda) return;
    
    const editorArea = document.getElementById(`editor-area-${partidaId}`);
    if (!editorArea) return;
    
    // Obtener el contenido editado
    const nuevoContenido = editorArea.innerHTML;
    
    // Guardar a través de AJAX
    guardarDescripcionPartida(partidaId, nuevoContenido, celda);
  }
  
  // Función para cancelar la edición
  function cancelarEdicion(partidaId) {
    console.log(`Cancelando edición de la partida ${partidaId}`);
    
    const celda = document.querySelector(`.partida-fila-1[data-partida-id="${partidaId}"] .descripcion-celda`);
    if (!celda) return;
    
    // Restaurar el contenido original
    celda.innerHTML = celda.dataset.originalContent || '';
    
    // Añadir overlay nuevamente
    const overlay = document.createElement('div');
    overlay.className = 'descripcion-overlay';
    celda.appendChild(overlay);
    
    // Manejar doble clic para iniciar edición
    overlay.addEventListener('dblclick', () => iniciarEdicion(partidaId, celda));
    
    // Quitar clase de edición
    celda.classList.remove('editando');
  }
  
  // Función para guardar la descripción mediante AJAX
  function guardarDescripcionPartida(partidaId, descripcion, celda) {
    // Obtener el token CSRF
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    
    // Preparar datos para la petición
    const formData = new FormData();
    formData.append('descripcion', descripcion);
    formData.append('csrf_token', csrfToken);
    
    // URL para la petición
    const url = `/presupuestos/partidas/${partidaId}/actualizar_descripcion`;
    
    // Mostrar indicador de carga
    celda.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Guardando...</div>';
    
    // Realizar la petición AJAX
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error al guardar la descripción');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Actualizar el contenido de la celda
        celda.dataset.originalContent = descripcion;
        celda.innerHTML = descripcion;
        
        // Añadir overlay nuevamente
        const overlay = document.createElement('div');
        overlay.className = 'descripcion-overlay';
        celda.appendChild(overlay);
        
        // Manejar doble clic para iniciar edición
        overlay.addEventListener('dblclick', () => iniciarEdicion(partidaId, celda));
        
        // Quitar clase de edición
        celda.classList.remove('editando');
        
        // Mostrar mensaje de éxito
        mostrarNotificacion('Descripción actualizada correctamente', 'success');
      } else {
        throw new Error(data.error || 'Error al guardar la descripción');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      
      // Restaurar el contenido original en caso de error
      cancelarEdicion(partidaId);
      
      // Mostrar mensaje de error
      mostrarNotificacion('Error al guardar la descripción: ' + error.message, 'danger');
    });
  }
  
  // Función para mostrar notificaciones
  function mostrarNotificacion(mensaje, tipo) {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} notification-toast`;
    notificacion.innerHTML = mensaje;
    notificacion.style.position = 'fixed';
    notificacion.style.top = '20px';
    notificacion.style.right = '20px';
    notificacion.style.zIndex = '9999';
    notificacion.style.minWidth = '300px';
    notificacion.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notificacion.style.transition = 'opacity 0.3s ease-in-out';
    
    // Añadir a la página
    document.body.appendChild(notificacion);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
      notificacion.style.opacity = '0';
      setTimeout(() => {
        document.body.removeChild(notificacion);
      }, 300);
    }, 3000);
  }
  
  console.log('Editor de texto en línea inicializado');
});
