# Instrucciones para Migrar Hojas de Trabajo a Presupuestos

Este documento proporciona instrucciones paso a paso para implementar el cambio en las hojas de trabajo, pasando de estar vinculadas a proyectos a estar vinculadas directamente a presupuestos.

## 1. Archivos Modificados

Los siguientes archivos han sido modificados:

- `app/models/hoja_trabajo.py`: Modelo actualizado para relacionarse con presupuestos
- `app/models/presupuesto.py`: Añadida relación con hojas de trabajo
- `app/routes/hoja_trabajo_routes.py`: Rutas actualizadas para trabajar con presupuestos
- `app/templates/hojas_trabajo/nueva.html`: Nueva plantilla para crear hojas desde presupuestos
- `app/templates/hojas_trabajo/por_presupuesto.html`: Nueva plantilla para listado por presupuesto
- `app/templates/hojas_trabajo/lista.html`: Plantilla general actualizada
- `app/templates/presupuestos/editar_pres.html`: Añadidos botones para gestionar hojas

## 2. Pasos para Implementar los Cambios

### Paso 1: Hacer copia de seguridad de la base de datos

```
copy app\data\app.db app\data\app.db.backup
```

### Paso 2: Colocar los nuevos archivos en su ubicación

Asegurar que todos los archivos modificados estén en sus respectivas carpetas.

### Paso 3: Ejecutar el script de migración

1. Abre una terminal cmd o PowerShell
2. Navega hasta el directorio principal del proyecto:
   ```
   cd C:\Users\Toni\Desktop\AM3.1
   ```
3. Ejecuta el script de migración:
   ```
   migrar_hojas_trabajo.bat
   ```
4. Espera a que el proceso termine y confirma que no hay errores

### Paso 4: Verificar la migración

1. Inicia la aplicación con:
   ```
   python run.py
   ```
2. Navega al listado de hojas de trabajo
3. Confirma que:
   - Las hojas existentes ahora están vinculadas a presupuestos
   - Las referencias siguen el formato correcto (referencia_presupuesto + HT)
   - Puedes acceder a las hojas desde los presupuestos

## 3. Solución de problemas

### Si hay hojas sin vincular a presupuestos

Si hay hojas que no pudieron vincularse automáticamente a presupuestos (porque no existían presupuestos relacionados en el mismo proyecto), deberás vincularlas manualmente:

1. Identifica la hoja huérfana en la interfaz (aparecerá con referencias al proyecto pero no al presupuesto)
2. Identifica el presupuesto al que debe vincularse
3. Usa una consulta SQL para actualizar la hoja:

```sql
UPDATE hojas_trabajo 
SET id_presupuesto = [id_del_presupuesto], 
    referencia = '[referencia_presupuesto]HT' 
WHERE id = [id_de_la_hoja];
```

### Si la aplicación falla al iniciar

1. Verifica los registros de error
2. Restaura la copia de seguridad de la base de datos:
   ```
   copy app\data\app.db.backup app\data\app.db
   ```
3. Revisa detalladamente los cambios de código para identificar el problema

## 4. Nuevas Funcionalidades

### Crear Hojas de Trabajo desde Presupuestos

1. Accede a un presupuesto en modo edición
2. Haz clic en el botón "Hoja Trabajo" en la barra superior
3. Completa los datos adicionales si es necesario
4. Guarda la nueva hoja de trabajo

### Ver Hojas de Trabajo de un Presupuesto

1. Accede a un presupuesto en modo edición
2. Haz clic en el icono de lista junto al botón "Hoja Trabajo"
3. Se mostrará un listado de todas las hojas asociadas al presupuesto

## 5. Para administradores

En caso de problemas graves con la migración o necesidad de revertir:

1. Detén la aplicación
2. Restaura la base de datos desde la copia de seguridad:
   ```
   copy app\data\app.db.backup app\data\app.db
   ```
3. Revierte los cambios en los archivos modificados
