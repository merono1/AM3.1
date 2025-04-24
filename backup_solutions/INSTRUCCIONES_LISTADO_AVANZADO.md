# Instrucciones para Listado Avanzado de Presupuestos

Este documento proporciona instrucciones paso a paso para configurar y utilizar el nuevo listado avanzado de presupuestos con filtros y campos adicionales.

## 1. Actualización de la Base de Datos

Antes de utilizar la nueva funcionalidad, es necesario actualizar la base de datos para añadir un nuevo campo requerido:

1. Localice el archivo `ejecutar_actualizacion.bat` en la carpeta principal.
2. Haga doble clic en este archivo para ejecutarlo.
3. Siga las instrucciones en pantalla. El script realizará las siguientes operaciones:
   - Añadir la columna `estado_workflow` a la tabla de presupuestos.
   - Crear una copia de seguridad de la base de datos antes de hacer cambios.
   - Proporcionar mensajes de confirmación o error.

Si desea comprobar si la actualización se realizó correctamente, ejecute el script `verificar_bd.py` con el comando:
```
python verificar_bd.py
```

## 2. Acceso al Listado Avanzado

Una vez actualizada la base de datos:

1. Inicie la aplicación con `python run.py`
2. Acceda desde el navegador a `http://localhost:5000`
3. En el menú principal, vaya a la sección "Presupuestos"
4. Seleccione "Listado Avanzado" del menú desplegable

## 3. Características del Listado Avanzado

### Campos Adicionales

El listado avanzado incluye los siguientes campos que no estaban disponibles en el listado básico:

- **Cliente:** Nombre del cliente asociado al proyecto.
- **Tipo de Proyecto:** Categoría del proyecto (Instalación, Mantenimiento, etc.).
- **Nombre del Proyecto:** Nombre descriptivo del proyecto.
- **Técnico Encargado:** Responsable asignado al presupuesto.
- **Aprobado:** Indicador de aprobación con interruptor para cambio rápido.
- **Fecha de Aprobación:** Fecha en que se aprobó el presupuesto.
- **Estado de Workflow:** Etapa actual del presupuesto en el flujo de trabajo.

### Filtros Avanzados

La sección de filtros avanzados permite buscar presupuestos por:

- **Cliente:** Filtrar por cliente específico.
- **Tipo de Proyecto:** Filtrar por categoría de proyecto.
- **Técnico Encargado:** Buscar presupuestos asignados a un técnico.
- **Estado de Workflow:** Filtrar por etapa del flujo de trabajo.
- **Fecha Desde/Hasta:** Filtrar por rango de fechas.
- **Aprobado:** Mostrar solo presupuestos aprobados o no aprobados.
- **Referencia:** Buscar por referencia de presupuesto.

### Funcionalidades Adicionales

- **Código de Colores:** Los presupuestos aprobados se muestran con fondo verde, los no aprobados con fondo rojo.
- **Actualización en Tiempo Real:** Los cambios en el estado de aprobación o workflow se guardan automáticamente.
- **Exportación:** Botón para exportar los resultados filtrados a CSV.

## 4. Solución de Problemas

Si encuentra algún problema con el listado avanzado:

1. **Error "no such column: estado_workflow":** 
   - Ejecute el script de actualización como se indica en el paso 1.
   - El listado básico seguirá funcionando correctamente aunque no haya ejecutado la migración.

2. **Problemas con la actualización de estados:** 
   - Asegúrese de que la base de datos se ha actualizado correctamente usando el verificador.
   - Si el problema persiste, intente con el script alternativo: `python fix_add_workflow_column.py`

3. **Los filtros no funcionan correctamente:** 
   - Confirme que ha aplicado la actualización de la base de datos.
   - Verifique que no hay errores en la consola del servidor.

Si persisten los problemas, puede volver al listado básico seleccionando "Listado Básico" en el menú desplegable de Presupuestos. El listado básico funcionará con o sin la actualización de base de datos.

## 5. Notas Técnicas

- Los estados de workflow disponibles son: En estudio, Estudiado, Revisión, Enviado, Pendiente de envío, Ejecutado, En ejecución.
- El cambio de estado de aprobación actualiza automáticamente la fecha de aprobación.
- La actualización de base de datos es segura y crea copias de seguridad automáticamente.
- Las vistas básicas han sido modificadas para ser tolerantes a fallos, por lo que seguirán funcionando incluso si no ejecuta la migración.
