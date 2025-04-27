# Gestor de Base de Datos AM3.1 - Guía de Usuario

## Introducción

El Gestor de Base de Datos de AM3.1 ha sido mejorado para proporcionar una experiencia más intuitiva y segura cuando se cambia entre bases de datos locales (SQLite) y remotas (PostgreSQL/Neon). Este documento explica las nuevas características y cómo utilizarlas.

## Características Principales

### 1. Indicador Claro del Tipo de Base de Datos

- **Banner de Color**: Verde para base de datos local, Azul para base de datos remota
- **Indicador Global**: Presente en todas las páginas de la aplicación
- **Actualización Automática**: El estado se actualiza cada 30 segundos

### 2. Reinicio de Aplicación Integrado

- **Botón de Reinicio**: Permite reiniciar la aplicación directamente desde la interfaz web
- **Sistema Automático**: La página se recarga automáticamente una vez completado el reinicio
- **Indicador de Progreso**: Muestra el estado del reinicio en tiempo real

### 3. Verificación de Base de Datos

- **Botón "Verificar"**: Comprueba qué base de datos está realmente en uso
- **Detección de Discrepancias**: Alerta cuando la configuración no coincide con la base de datos real
- **Información Detallada**: Muestra versión, número de tablas y otros detalles importantes

## Cómo Usar

### Cambiar Entre Bases de Datos

1. Acceda a **Gestión de Base de Datos** haciendo clic en el banner superior o navegando a `/db-manager/`
2. Seleccione una de las siguientes opciones:
   - **Usar Base de Datos Local**: Para trabajar con SQLite local
   - **Usar Base de Datos Neon**: Para trabajar con PostgreSQL en la nube
3. Haga clic en **Reiniciar aplicación ahora** para aplicar los cambios

### Verificar Estado de la Base de Datos

1. Haga clic en el botón **Verificar** en el banner superior
2. Un modal mostrará información detallada sobre la base de datos en uso
3. Si se detecta una discrepancia, aparecerá un botón para reiniciar la aplicación

### Sincronizar Bases de Datos

1. **Descargar de Neon**: Copia la base de datos remota a local
2. **Subir a Neon**: Sincroniza la base de datos local con la remota
3. Las operaciones son seguras y crean copias de seguridad automáticamente

## Resolución de Problemas

### La aplicación muestra "Discrepancia detectada"

Esto ocurre cuando la configuración no coincide con la base de datos real en uso. Solución:
1. Haga clic en **Reiniciar aplicación ahora**
2. Si persiste, verifique los archivos de configuración de la base de datos

### Error al verificar la base de datos

Si aparece un error al hacer clic en "Verificar":
1. Intente reiniciar la aplicación manualmente
2. Verifique que la base de datos está accesible
3. Revise los logs para más detalles (`logs/app.log`)

## Notas Importantes

- El cambio entre bases de datos requiere reiniciar la aplicación
- Se recomienda hacer un backup antes de cambiar entre bases de datos
- El banner global puede ocultarse temporalmente haciendo clic en la X, pero reaparecerá en la próxima sesión

## Desarrolladores

Para más detalles técnicos sobre la implementación, consulte el archivo `docs/soluciones/soluciones_8_gestor_bd_mejorado.md`.
