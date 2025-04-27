# Soluciones 7: Sistema de Gestión de Base de Datos Local/Remota

## 1. Funcionalidad de Gestión de Base de Datos

### 1.1 Descripción General
Se ha implementado un sistema que permite:
- Descargar la base de datos de PostgreSQL (Neon) a SQLite local
- Trabajar de forma local y sin conexión
- Sincronizar los cambios locales con la base de datos remota
- Alternar entre modo local y remoto según necesidades

### 1.2 Archivos Implementados
- **`app/services/db_backup_service.py`**: Servicio principal para gestión de bases de datos
- **`app/routes/db_manager_routes.py`**: Controlador con rutas para gestionar operaciones
- **`app/templates/db_manager/index.html`**: Interfaz de usuario para la gestión
- **Modificaciones en `app/__init__.py`**: Inicialización del servicio
- **Modificaciones en `app/routes/__init__.py`**: Registro del nuevo blueprint
- **Modificaciones en `app/templates/index.html`**: Acceso destacado desde la página principal

## 2. Funcionalidades Principales

### 2.1 Descarga de Base de Datos (PostgreSQL → SQLite)
**Proceso**:
1. Se crea automáticamente una copia de seguridad de la BD local si existe
2. Se obtienen los metadatos y estructura de tablas de PostgreSQL
3. Se crean las tablas equivalentes en SQLite
4. Se transfieren los datos tabla por tabla
5. Se registra el proceso con timestamps para auditoría

**Implementación**:
```python
def download_postgres_to_sqlite(self):
    """Descarga la base de datos PostgreSQL a SQLite local."""
    # Crear backup antes de sobreescribir
    if self.local_db_path.exists():
        self._backup_sqlite_db()
    
    # Crear motores para ambas bases de datos
    pg_engine = self._get_postgres_engine()
    sqlite_engine = self._get_sqlite_engine()
    
    # Obtener metadatos y tablas de PostgreSQL
    metadata = MetaData()
    metadata.reflect(bind=pg_engine)
    
    # Crear todas las tablas en SQLite
    metadata.create_all(sqlite_engine)
    
    # Transferir datos tabla por tabla
    for table_name, table in metadata.tables.items():
        # Leer datos de PostgreSQL
        with pg_engine.connect() as pg_conn:
            result = pg_conn.execute(table.select())
            rows = result.fetchall()
        
        # Insertar en SQLite
        if rows:
            # [código para inserción de datos]
```

### 2.2 Sincronización de Cambios (SQLite → PostgreSQL)
**Proceso**:
1. Se verifica la existencia de la base de datos local
2. Se obtienen los metadatos y estructura de SQLite
3. Se transfieren los datos a PostgreSQL tabla por tabla
4. Se mantiene un log detallado del proceso

**Implementación**:
```python
def upload_sqlite_to_postgres(self):
    """Sube la base de datos SQLite local a PostgreSQL."""
    # Verificar que existe la base de datos local
    if not self.local_db_path.exists():
        return False, f"No se encontró la base de datos local en {self.local_db_path}"
    
    # Crear motores para ambas bases de datos
    sqlite_engine = self._get_sqlite_engine()
    pg_engine = self._get_postgres_engine()
    
    # Obtener metadatos de SQLite
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    
    # Transferir datos tabla por tabla
    for table_name, table in metadata.tables.items():
        # [código para transferencia de datos]
```

### 2.3 Cambio entre Modos (Local ↔ Remoto)
**Funcionalidades**:
- Cambio a modo local: configura la aplicación para usar SQLite
- Cambio a modo remoto: configura la aplicación para usar PostgreSQL
- Información de estado: muestra la configuración actual

**Nota importante**: El cambio entre modos requiere reiniciar la aplicación para que se aplique correctamente.

## 3. Interfaz de Usuario

### 3.1 Página Principal
Se ha añadido un banner destacado en la página de inicio para acceder rápidamente al gestor de base de datos, con el objetivo de que sea lo primero que vea el usuario al iniciar la aplicación.

### 3.2 Panel de Gestión de Base de Datos
**Componentes**:
- **Estado actual**: Muestra información sobre la base de datos en uso
- **Descarga de BD**: Permite descargar la base de datos remota a local
- **Sincronización**: Permite subir los cambios locales a la BD remota
- **Cambio de modo**: Opciones para alternar entre local y remoto

**Actualización automática**:
La interfaz se actualiza cada 30 segundos para mostrar el estado actual de la conexión a la base de datos.

## 4. Sistema de Copias de Seguridad

### 4.1 Backups Automáticos
Antes de sobrescribir la base de datos local al descargar de PostgreSQL, se crea automáticamente una copia de seguridad con timestamp:

```python
def _backup_sqlite_db(self):
    """Crear backup de la base de datos SQLite."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = self.backup_dir / f"app_db_backup_{timestamp}.db"
    
    # Copiar archivo
    import shutil
    shutil.copy2(self.local_db_path, backup_path)
    
    # Guardar referencia al último backup
    self._last_backup_path = backup_path
    
    logger.info(f"Backup creado en: {backup_path}")
    return backup_path
```

### 4.2 Restauración
Si ocurre un error durante la descarga, se restaura automáticamente el último backup:

```python
def _restore_sqlite_backup(self):
    """Restaurar el último backup de SQLite."""
    if hasattr(self, '_last_backup_path') and self._last_backup_path.exists():
        import shutil
        shutil.copy2(self._last_backup_path, self.local_db_path)
        logger.info(f"Restaurado backup desde: {self._last_backup_path}")
        return True
    return False
```

## 5. Comandos CLI

Se han implementado comandos para la terminal que permiten realizar estas operaciones sin necesidad de la interfaz web:

```bash
# Descargar base de datos
flask download-db

# Subir base de datos
flask upload-db
```

## 6. Recomendaciones de Uso

### 6.1 Cuándo usar base de datos local
- Cuando se trabaja sin conexión a internet
- Para operaciones que requieren mejor rendimiento
- Durante el desarrollo de nuevas funcionalidades
- En entornos con conexión inestable

### 6.2 Cuándo usar base de datos remota (Neon)
- Cuando se necesita que los datos estén disponibles para múltiples usuarios
- Para garantizar la persistencia en la nube
- En producción o demo con clientes
- Cuando se trabaja desde diferentes equipos

### 6.3 Mejores prácticas
- Sincronizar regularmente los cambios locales con la base de datos remota
- Crear copias de seguridad antes de operaciones importantes
- Verificar el estado de la conexión antes de realizar cambios masivos
- Reiniciar la aplicación después de cambiar entre modos

## 7. Posibles Mejoras Futuras

1. **Sincronización selectiva**: Permitir seleccionar qué tablas sincronizar
2. **Resolución de conflictos**: Mejorar la gestión cuando hay cambios en ambas BDs
3. **Programación de sincronización**: Sincronización automática programada
4. **Encriptación de datos locales**: Mayor seguridad para datos sensibles
5. **Interfaz de gestión de backups**: Visualizar y restaurar backups anteriores
6. **Migración incremental**: Optimizar transferencia para solo enviar cambios
7. **Notificaciones**: Alertas cuando hay cambios pendientes de sincronizar

## 8. Solución Alternativa para Descarga/Subida de Base de Datos

Se ha implementado un sistema alternativo más robusto para la transferencia de datos entre PostgreSQL y SQLite que utiliza conexiones directas a las bases de datos en lugar de SQLAlchemy.

### 8.1 Scripts Independientes
- **`db_download.py`**: Script independiente para descargar la base de datos
- **`db_upload.py`**: Script independiente para subir la base de datos
- **`descargar_bd.bat`**: Batch para ejecutar fácilmente la descarga
- **`subir_bd.bat`**: Batch para ejecutar fácilmente la subida

### 8.2 Método Directo de Transferencia
El nuevo método resuelve varios problemas del enfoque original:
- Maneja directamente los tipos de datos entre PostgreSQL y SQLite
- Gestiona correctamente los valores nulos
- Evita errores relacionados con SQLAlchemy
- Proporciona mejor información sobre el progreso
- Permite transacciones por lotes para mejor rendimiento

### 8.3 Uso de los Scripts Independientes
Para usuarios que experimentan problemas con la interfaz web:

1. **Descargar base de datos**:
   - Ejecutar `descargar_bd.bat` desde el explorador de archivos
   - Esperar a que el proceso complete
   - La base de datos se descarga a `instance/app.db` (o la ruta configurada en `.env`)

2. **Subir base de datos**:
   - Ejecutar `subir_bd.bat` desde el explorador de archivos
   - Confirmar la operación cuando se solicite
   - Esperar a que el proceso complete

3. **Uso desde terminal**:
   ```batch
   # Descargar (con entorno virtual activo)
   python db_download.py
   
   # Subir (con entorno virtual activo)
   python db_upload.py
   ```

### 8.4 Ventajas de Este Enfoque
- Funcionamiento independiente de Flask y SQLAlchemy
- Mejor manejo de errores y situaciones excepcionales
- Mayor velocidad en la transferencia de datos
- Registro detallado del proceso
- Backups automáticos de seguridad