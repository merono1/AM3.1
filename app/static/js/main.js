/**
 * main.js - Funciones comunes para la aplicación AM3.1
 * 
 * Este archivo contiene funciones JavaScript reutilizables para toda la aplicación,
 * evitando duplicaciones y mejorando la coherencia del código.
 */

// ===== INICIALIZACIÓN =====

/**
 * Inicializa componentes comunes cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar tooltips de Bootstrap
  initTooltips();
  
  // Inicializar filtros de tablas
  initTableFilters();
  
  // Inicializar validación de formularios
  initFormValidation();
  
  // Inicializar botones de exportación 
  initExportButtons();
  
  console.log('AM3.1: Inicialización del DOM completada');
});

// ===== UTILIDADES DE UI =====

/**
 * Inicializa los tooltips de Bootstrap en la página
 */
function initTooltips() {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Inicializa filtros para tablas
 */
function initTableFilters() {
  document.querySelectorAll('.table-filter').forEach(function(input) {
    input.addEventListener('keyup', function() {
      var tableId = this.getAttribute('data-table');
      var table = document.getElementById(tableId);
      if (!table) return;
      
      var searchText = this.value.toLowerCase();
      var rows = table.querySelectorAll('tbody tr');
      
      rows.forEach(function(row) {
        var textFound = false;
        row.querySelectorAll('td').forEach(function(cell) {
          if (cell.textContent.toLowerCase().indexOf(searchText) > -1) {
            textFound = true;
          }
        });
        row.style.display = textFound ? '' : 'none';
      });
    });
  });
}

/**
 * Inicializa botones para exportar tablas a CSV
 */
function initExportButtons() {
  document.querySelectorAll('[data-export-table]').forEach(function(button) {
    button.addEventListener('click', function() {
      var tableId = this.getAttribute('data-export-table');
      var filename = this.getAttribute('data-export-filename') || tableId + '.csv';
      exportTableToCSV(tableId, filename);
    });
  });
}

/**
 * Exporta una tabla HTML a un archivo CSV
 * @param {string} tableId - ID de la tabla a exportar
 * @param {string} filename - Nombre del archivo CSV a generar
 */
function exportTableToCSV(tableId, filename) {
  var table = document.getElementById(tableId);
  if (!table) {
    console.error('Tabla no encontrada:', tableId);
    return;
  }
  
  var rows = table.querySelectorAll('tr');
  var csv = [];
  
  for (var i = 0; i < rows.length; i++) {
    var row = [], cols = rows[i].querySelectorAll('td, th');
    
    for (var j = 0; j < cols.length; j++) {
      // Excluir la columna de acciones (normalmente la última)
      if (j === cols.length - 1 && cols[j].querySelector('.btn-group')) continue;
      
      // Limpiar el texto (eliminar saltos de línea y comas)
      var text = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, ' ').replace(/,/g, ';');
      row.push('"' + text + '"');
    }
    
    csv.push(row.join(','));
  }
  
  // Crear el archivo CSV
  var csvFile = new Blob([csv.join('\n')], {type: 'text/csv'});
  
  // Descargar el archivo
  var downloadLink = document.createElement('a');
  downloadLink.download = filename;
  downloadLink.href = window.URL.createObjectURL(csvFile);
  downloadLink.style.display = 'none';
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
}

// ===== VALIDACIÓN DE FORMULARIOS =====

/**
 * Inicializa la validación básica de formularios
 */
function initFormValidation() {
  // Añadir validación al enviar el formulario
  document.querySelectorAll('form[data-validate="true"]').forEach(function(form) {
    form.addEventListener('submit', function(event) {
      if (!validateForm(this.id)) {
        event.preventDefault();
        event.stopPropagation();
      }
    });
  });
  
  // Validación en tiempo real para campos obligatorios
  document.querySelectorAll('input[required], select[required], textarea[required]').forEach(function(field) {
    field.addEventListener('blur', function() {
      validateField(this);
    });
    
    field.addEventListener('change', function() {
      validateField(this);
    });
  });
}

/**
 * Valida un formulario completo
 * @param {string} formId - ID del formulario a validar
 * @returns {boolean} - true si el formulario es válido, false en caso contrario
 */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;
  
  // Obtener todos los campos obligatorios
  var requiredFields = form.querySelectorAll('[required]');
  var isValid = true;
  
  // Validar cada campo obligatorio
  requiredFields.forEach(function(field) {
    if (!validateField(field)) {
      isValid = false;
    }
  });
  
  return isValid;
}

/**
 * Valida un campo individual
 * @param {HTMLElement} field - Campo a validar
 * @returns {boolean} - true si el campo es válido, false en caso contrario
 */
function validateField(field) {
  var isValid = true;
  
  // Validar según el tipo de campo
  if (field.type === 'text' || field.type === 'textarea' || field.type === 'email' || 
      field.type === 'password' || field.type === 'tel' || field.type === 'number' || 
      field.type === 'url' || field.tagName.toLowerCase() === 'textarea') {
    isValid = field.value.trim() !== '';
  } else if (field.type === 'select-one') {
    isValid = field.value !== '';
  } else if (field.type === 'checkbox') {
    isValid = field.checked;
  }
  
  // Aplicar estilos de validación
  if (!isValid) {
    field.classList.add('is-invalid');
    
    // Añadir mensaje de error si no existe
    var feedbackDiv = field.nextElementSibling;
    if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
      var label = field.closest('.mb-3')?.querySelector('.form-label')?.textContent || 'Este campo';
      feedbackDiv = document.createElement('div');
      feedbackDiv.className = 'invalid-feedback';
      feedbackDiv.textContent = label.replace('*', '') + ' es obligatorio';
      field.parentNode.insertBefore(feedbackDiv, field.nextSibling);
    }
  } else {
    field.classList.remove('is-invalid');
  }
  
  return isValid;
}

// ===== UTILIDADES PARA DIRECCIÓN =====

/**
 * Copia los datos de dirección de un cliente al formulario de proyecto
 * @param {number} clienteId - ID del cliente
 * @param {Object} clientesData - Datos de todos los clientes
 */
function copiarDireccionCliente(clienteId, clientesData) {
  var clienteData = clientesData[clienteId];
  if (!clienteData) {
    alert('No se pudo obtener la información de dirección del cliente seleccionado.');
    return;
  }
  
  // Comprobar que existen los campos de dirección
  if (!document.getElementById('tipo_via')) {
    alert('Error: No se encontraron los campos de dirección en el formulario.');
    return;
  }
  
  // Rellenar campos de dirección
  document.getElementById('tipo_via').value = clienteData.tipo_via || '';
  document.getElementById('nombre_via').value = clienteData.nombre_via || '';
  document.getElementById('numero_via').value = clienteData.numero_via || '';
  document.getElementById('puerta').value = clienteData.puerta || '';
  document.getElementById('codigo_postal').value = clienteData.codigo_postal || '';
  document.getElementById('poblacion').value = clienteData.poblacion || '';
  
  alert('Dirección del cliente copiada con éxito.');
}

// ===== FUNCIONES PARA CKEditor =====

/**
 * Inicializa CKEditor en un campo de texto dado
 * @param {string} elementId - ID del elemento donde inicializar CKEditor
 * @param {Object} options - Opciones personalizadas para CKEditor
 */
function initCKEditor(elementId, options = {}) {
  if (typeof ClassicEditor === 'undefined') {
    console.error('CKEditor no está disponible. Asegúrate de cargar el script.');
    return;
  }
  
  const defaultOptions = {
    toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|', 'indent', 'outdent', '|', 'blockQuote', 'insertTable', 'undo', 'redo'],
    placeholder: 'Escribe aquí...',
    language: 'es'
  };
  
  const mergedOptions = {...defaultOptions, ...options};
  
  ClassicEditor
    .create(document.getElementById(elementId), mergedOptions)
    .then(editor => {
      console.log('CKEditor inicializado correctamente en:', elementId);
      window.editors = window.editors || {};
      window.editors[elementId] = editor;
    })
    .catch(error => {
      console.error('Error al inicializar CKEditor:', error);
    });
}

// ===== UTILIDADES NUMÉRICAS =====

/**
 * Formatea un número como importe en euros
 * @param {number} amount - Cantidad a formatear
 * @param {number} decimals - Número de decimales (por defecto 2)
 * @returns {string} - Importe formateado
 */
function formatCurrency(amount, decimals = 2) {
  if (isNaN(amount)) return '0,00 €';
  return amount.toFixed(decimals).replace('.', ',') + ' €';
}

/**
 * Calcula el total de una partida multiplicando cantidad por precio
 * @param {number} cantidad - Cantidad
 * @param {number} precio - Precio unitario
 * @returns {number} - Total calculado
 */
function calcularTotal(cantidad, precio) {
  const cantidadNum = parseFloat(cantidad) || 0;
  const precioNum = parseFloat(precio) || 0;
  return cantidadNum * precioNum;
}

/**
 * Calcula el precio final aplicando un margen al total
 * @param {number} total - Total sin margen
 * @param {number} margen - Porcentaje de margen
 * @returns {number} - Precio final con margen
 */
function calcularFinal(total, margen) {
  const totalNum = parseFloat(total) || 0;
  const margenNum = parseFloat(margen) || 0;
  return totalNum * (1 + margenNum / 100);
}
