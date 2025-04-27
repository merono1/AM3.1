# Estandarización HTML - Abril 2025

## Resumen de cambios realizados

Se ha llevado a cabo una refactorización completa de los archivos HTML para mejorar la coherencia, eliminar código duplicado y estandarizar la estética de la aplicación. Los cambios se han organizado en varias categorías clave para facilitar su comprensión.

## 1. Plantillas base y layouts

### Mejoras implementadas:
- **Plantilla base unificada**: Se ha actualizado `base.html` para que actúe como única fuente de verdad para la estructura común de todas las páginas.
- **Nueva plantilla para errores**: Se ha creado `error_base.html` específica para páginas de error con un diseño cohesivo.
- **Estructura de bloques estandarizada**: Implementación de un conjunto coherente de bloques (`title`, `page_title`, `page_header`, `page_actions`, `content`, `scripts`).

### Beneficios:
- Mayor coherencia visual entre todas las páginas de la aplicación
- Reducción significativa de código duplicado
- Experiencia de usuario mejorada para páginas de error

## 2. Componentes y macros

### Mejoras implementadas:
- **Biblioteca de componentes expandida**: Se ha ampliado `components.html` con numerosos componentes reutilizables.
- **Formularios predefinidos**: Creación de macros para formularios completos (`client_form`, `project_form`).
- **Componentes para tablas y datos**: Nuevo macro `data_table` para estandarizar la presentación de datos tabulares.
- **Componentes de alerta y feedback**: Macros para alertas, badges y modales consistentes.

### Beneficios:
- Escritura más rápida de nuevas páginas
- Mayor consistencia en formularios y listas
- Reducción del esfuerzo de mantenimiento

## 3. CSS y estilos

### Mejoras implementadas:
- **Sistema de estilos centralizado**: Reorganización de `styles.css` con variables y componentes claros.
- **Variables CSS**: Implementación de variables para colores, espaciado y otros valores clave.
- **Soporte para temas**: Base para futura implementación de modo oscuro.
- **CSS específico para integraciones**: Archivo dedicado para CKEditor.

### Beneficios:
- Apariencia más consistente en toda la aplicación
- Reducción de conflictos de estilos
- Base para implementar diferentes temas en el futuro

## 4. JavaScript centralizado

### Mejoras implementadas:
- **Biblioteca JS centralizada**: Creación de `main.js` con funciones comunes.
- **Funciones de utilidad**: Implementación de utilidades para validación, exportación, filtrado, etc.
- **Inicialización automática**: Componentes como tooltips o filtros se inicializan automáticamente.

### Beneficios:
- Eliminación de código JavaScript duplicado
- Comportamiento consistente de componentes interactivos
- Mayor facilidad para implementar nuevas funcionalidades

## 5. Páginas actualizadas

### Formularios:
- **Clientes**: Formularios de nuevo y edición estandarizados
- **Proyectos**: Formularios con validación coherente

### Listas:
- **Clientes**: Lista con filtrado, exportación y acciones estandarizadas
- **Proyectos**: Lista con presentación mejorada y modales coherentes

### Páginas de error:
- **404**: Diseño mejorado con opciones de navegación
- **500**: Presentación clara del error con información útil
- **Database**: Información detallada sobre problemas de conexión

## Guía de implementación para nuevas páginas

### 1. Estructura de una página estándar

```html
{% extends 'layout/base.html' %}
{% from 'layout/components.html' import [componentes_necesarios] %}

{% block title %}AM3.1 - [Título de la página]{% endblock %}

{% block page_title %}[Título principal]{% endblock %}

{% block page_actions %}
<div class="col text-end">
  <!-- Botones de acción principales -->
</div>
{% endblock %}

{% block content %}
  <!-- Contenido principal de la página -->
{% endblock %}

{% block scripts %}
<script>
  // JavaScript específico de la página
</script>
{% endblock %}
```

### 2. Uso de componentes predefinidos

#### Formularios:
```html
{{ form_group('nombre_campo', 'Etiqueta', type='text', required=true) }}
```

#### Tablas:
```html
{% call data_table(id='tabla-id', columns=[...], rows=[...]) %}
  <!-- Contenido personalizado para cada fila -->
{% endcall %}
```

#### Modales:
```html
{{ confirmation_modal(id='modal-id', title='Título', message='Mensaje', action_url='url') }}
```

## Próximos pasos recomendados

1. **Completar la estandarización**: Aplicar los mismos principios a las páginas restantes.
2. **Documentación de componentes**: Crear una página de documentación para desarrolladores.
3. **Pruebas de usabilidad**: Evaluar la experiencia de usuario con las nuevas plantillas.
4. **Implementación de modo oscuro**: Aprovechar las variables CSS para crear un modo oscuro.
5. **Optimización para móviles**: Mejorar la experiencia en dispositivos móviles.

## Conclusión

La estandarización realizada ha eliminado inconsistencias, reducido código duplicado y mejorado la estética general de la aplicación. Esta base sólida facilitará el desarrollo futuro y mejorará la experiencia tanto para usuarios como para desarrolladores.

---

*Documento preparado por: Claude - Abril 2025*