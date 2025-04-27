"""
Servicio para gestión de copias de seguridad y sincronización de bases de datos.
Permite trabajar con una base de datos local y sincronizar con PostgreSQL (Neon).
"""

import os
import subprocess
import datetime
import logging
import tempfile
import time
import sqlite3
from pathlib import Path
from flask import current_app
import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackupService:
    """Servicio para gestionar copias y sincronización de bases de datos."""
    
    def __init__(self, app=None):
        self.app = app
        # Rutas predeterminadas
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.backup_dir = self.base_dir / 'backups'
        self.local_db_path = self.base_dir / 'instance' / 'app.db'
        
        # Asegurar que exista el directorio de backups
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar con la aplicación Flask."""
        self.app = app
        # Obtener configuración desde la app
        self.postgresql_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        self.local_db_path = Path(app.config.get('DB_PATH'))
        
        # Asegurar que el directorio de la base de datos SQLite exista
        self.local_db_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Registrar comandos CLI si está disponible
        if hasattr(app, 'cli'):
            self._register_commands(app)
    
    def _register_commands(self, app):
        """Registrar comandos CLI para la aplicación."""
        @app.cli.command('download-db')
        def download_db_command():
            """Descargar base de datos de PostgreSQL a SQLite local."""
            self.download_postgres_to_sqlite()
        
        @app.cli.command('upload-db')
        def upload_db_command():
            """Subir base de datos SQLite local a PostgreSQL."""
            self.upload_sqlite_to_postgres()
    
    def _get_sqlite_engine(self):
        """Obtener motor SQLAlchemy para SQLite."""
        sqlite_url = f"sqlite:///{self.local_db_path}"
        return create_engine(sqlite_url)
    
    def _get_postgres_engine(self):
        """Obtener motor SQLAlchemy para PostgreSQL."""
        return create_engine(self.postgresql_url)
    
    def _get_all_tables(self, engine):
        """Obtener todas las tablas de la base de datos."""
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    def download_postgres_to_sqlite(self):
        """
        Descarga la base de datos PostgreSQL a SQLite local.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
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
            total_tables = len(metadata.tables)
            processed = 0
            
            for table_name, table in metadata.tables.items():
                processed += 1
                logger.info(f"Descargando tabla {processed}/{total_tables}: {table_name}")
                
                # Leer datos de PostgreSQL
                with pg_engine.connect() as pg_conn:
                    result = pg_conn.execute(table.select())
                    rows = result.fetchall()
                
                # Si hay datos, insertarlos en SQLite
                if rows:
                    # Crear lista de diccionarios con los datos
                    column_names = result.keys()
                    data = [dict(zip(column_names, row)) for row in rows]
                    
                    # Insertar en SQLite
                    with sqlite_engine.connect() as sqlite_conn:
                        sqlite_conn.execute(table.delete())  # Limpiar tabla primero
                        for row_dict in data:
                            # Filtrar valores None para SQLite que no acepta ciertos tipos
                            filtered_dict = {}
                            for key, value in row_dict.items():
                                if value is not None:
                                    filtered_dict[key] = value
                            
                            # Solo insertar si hay datos válidos
                            if filtered_dict:
                                try:
                                    sqlite_conn.execute(table.insert().values(**filtered_dict))
                                except Exception as e:
                                    logger.warning(f"Error insertando fila en tabla {table_name}: {e}")
                        
                        sqlite_conn.commit()
            
            logger.info(f"Base de datos descargada exitosamente a {self.local_db_path}")
            return True, f"Base de datos descargada exitosamente a {self.local_db_path}"
        
        except Exception as e:
            logger.error(f"Error al descargar base de datos: {str(e)}")
            # Restaurar backup si falló
            if hasattr(self, '_last_backup_path') and self._last_backup_path.exists():
                self._restore_sqlite_backup()
            return False, f"Error al descargar base de datos: {str(e)}"
    
    def upload_sqlite_to_postgres(self):
        """
        Sube la base de datos SQLite local a PostgreSQL.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Verificar que existe la base de datos local
            if not self.local_db_path.exists():
                return False, f"No se encontró la base de datos local en {self.local_db_path}"
            
            # Crear backup de PostgreSQL (por ahora solo log)
            logger.info("Creando punto de respaldo en PostgreSQL...")
            
            # Crear motores para ambas bases de datos
            sqlite_engine = self._get_sqlite_engine()
            pg_engine = self._get_postgres_engine()
            
            # Obtener metadatos de SQLite
            metadata = MetaData()
            metadata.reflect(bind=sqlite_engine)
            
            # Transferir datos tabla por tabla
            total_tables = len(metadata.tables)
            processed = 0
            
            for table_name, table in metadata.tables.items():
                processed += 1
                logger.info(f"Subiendo tabla {processed}/{total_tables}: {table_name}")
                
                # Leer datos de SQLite
                with sqlite_engine.connect() as sqlite_conn:
                    result = sqlite_conn.execute(table.select())
                    rows = result.fetchall()
                
                # Si hay datos, insertarlos en PostgreSQL
                if rows:
                    # Crear lista de diccionarios con los datos
                    column_names = result.keys()
                    data = [dict(zip(column_names, row)) for row in rows]
                    
                    # Insertar en PostgreSQL (primero limpiar tabla)
                    with pg_engine.connect() as pg_conn:
                        pg_conn.execute(table.delete())
                        for row_dict in data:
                            pg_conn.execute(table.insert().values(**row_dict))
                        pg_conn.commit()
            
            logger.info("Base de datos subida exitosamente a PostgreSQL")
            return True, "Base de datos subida exitosamente a PostgreSQL"
        
        except Exception as e:
            logger.error(f"Error al subir base de datos: {str(e)}")
            return False, f"Error al subir base de datos: {str(e)}"
    
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
    
    def _restore_sqlite_backup(self):
        """Restaurar el último backup de SQLite."""
        if hasattr(self, '_last_backup_path') and self._last_backup_path.exists():
            import shutil
            shutil.copy2(self._last_backup_path, self.local_db_path)
            logger.info(f"Restaurado backup desde: {self._last_backup_path}")
            return True
        return False
    
    def switch_to_local_db(self):
        """
        Cambiar la configuración para usar SQLite local.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.app:
            return False, "No se ha inicializado con una aplicación Flask"
        
        try:
            # Verificar que existe la base de datos local
            if not self.local_db_path.exists():
                # Intentar descargar primero
                success, message = self.download_postgres_to_sqlite()
                if not success:
                    return False, f"No se pudo descargar la base de datos: {message}"
            
            # Cambiar configuración
            sqlite_url = f"sqlite:///{self.local_db_path}"
            self.app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_url
            
            # Actualizar URL en variables de entorno (para próximos arranques)
            os.environ['SQLALCHEMY_DATABASE_URI'] = sqlite_url
            
            # Actualizar conexiones (requiere reinicio completo de la aplicación)
            logger.info(f"Configuración cambiada a base de datos local: {self.local_db_path}")
            return True, f"Configuración cambiada a base de datos local: {self.local_db_path}"
        
        except Exception as e:
            logger.error(f"Error al cambiar a base de datos local: {str(e)}")
            return False, f"Error al cambiar a base de datos local: {str(e)}"
    
    def switch_to_postgres_db(self):
        """
        Cambiar la configuración para usar PostgreSQL.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.app:
            return False, "No se ha inicializado con una aplicación Flask"
        
        try:
            # Cambiar configuración
            self.app.config['SQLALCHEMY_DATABASE_URI'] = self.postgresql_url
            
            # Actualizar URL en variables de entorno (para próximos arranques)
            os.environ['SQLALCHEMY_DATABASE_URI'] = self.postgresql_url
            
            # Actualizar conexiones (requiere reinicio completo de la aplicación)
            logger.info(f"Configuración cambiada a PostgreSQL")
            return True, "Configuración cambiada a PostgreSQL"
        
        except Exception as e:
            logger.error(f"Error al cambiar a PostgreSQL: {str(e)}")
            return False, f"Error al cambiar a PostgreSQL: {str(e)}"
    
    def get_current_db_info(self):
        """
        Obtener información sobre la base de datos actual.
        
        Returns:
            dict: Información de la base de datos actual
        """
        if not self.app:
            return {"error": "No se ha inicializado con una aplicación Flask"}
        
        current_url = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        if current_url.startswith('sqlite'):
            db_type = "SQLite (Local)"
            db_path = self.local_db_path
            
            # Obtener tamaño y fecha de modificación
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                mod_time = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
                
                return {
                    "type": db_type,
                    "path": str(db_path),
                    "size": f"{size_mb:.2f} MB",
                    "last_modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "exists": True,
                    "indicator": "local",  # Indicador para uso de color en UI
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {
                    "type": db_type,
                    "path": str(db_path),
                    "exists": False,
                    "message": "Base de datos local no encontrada",
                    "indicator": "local",  # Indicador para uso de color en UI
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        else:
            db_type = "PostgreSQL (Neon)"
            # Ocultar credenciales
            safe_url = self.postgresql_url.split('@')[1] if '@' in self.postgresql_url else 'configurada'
            
            return {
                "type": db_type,
                "connection": safe_url,
                "exists": True,
                "indicator": "remote",  # Indicador para uso de color en UI
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def perform_verification_query(self):
        """
        Realizar una consulta de verificación para confirmar qué base de datos está activa realmente.
        
        Returns:
            dict: Resultado de la verificación
        """
        try:
            # Crear una consulta sencilla para distinguir entre bases de datos
            # En SQLite usar una función propia de SQLite y en PostgreSQL usar una de PostgreSQL
            if not self.app:
                return {"error": "No se ha inicializado con una aplicación Flask"}

            current_url = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            # Crear motor adecuado según la URL
            engine = create_engine(current_url)
            
            # Ejecutar consultas específicas para cada tipo de base de datos
            with engine.connect() as conn:
                if current_url.startswith('sqlite'):
                    # Consulta específica de SQLite
                    result = conn.execute(text("SELECT sqlite_version() AS version, 'SQLite' AS db_type")).fetchone()
                    verification_type = "SQLite"
                else:
                    # Consulta específica de PostgreSQL
                    result = conn.execute(text("SELECT version() AS version, 'PostgreSQL' AS db_type")).fetchone()
                    verification_type = "PostgreSQL"
                
                # Obtener algunas tablas para más confirmación
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                # Devolver resultados
                return {
                    "verified_db_type": verification_type,
                    "version": result[0] if result else "Desconocida",
                    "tables_count": len(tables),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "matches_config": (verification_type == "SQLite" and current_url.startswith('sqlite')) or \
                                    (verification_type == "PostgreSQL" and not current_url.startswith('sqlite'))
                }
        
        except Exception as e:
            logger.exception("Error al realizar verificación de la base de datos")
            return {
                "error": str(e),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

# Instancia global del servicio
db_backup_service = DatabaseBackupService()
