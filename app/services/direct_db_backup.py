"""
Servicio para transferencia directa de datos entre PostgreSQL y SQLite.
Usa instrucciones SQL directas en lugar de SQLAlchemy para mayor compatibilidad.
"""

import os
import sqlite3
import psycopg2
import logging
import datetime
import shutil
from pathlib import Path
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectDatabaseTransfer:
    """Clase para transferencia directa de datos entre PostgreSQL y SQLite."""
    
    def __init__(self, pg_url=None, sqlite_path=None):
        """
        Inicializar servicio con conexiones a bases de datos.
        
        Args:
            pg_url: URL de conexión a PostgreSQL
            sqlite_path: Ruta al archivo SQLite
        """
        self.pg_url = pg_url
        self.sqlite_path = Path(sqlite_path) if sqlite_path else None
        self.backup_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'backups'
        
        # Asegurar que exista directorio de backups
        self.backup_dir.mkdir(exist_ok=True, parents=True)
    
    def _connect_postgres(self):
        """Establecer conexión a PostgreSQL."""
        try:
            # Extraer parámetros de la URL para poder añadir más configuraciones
            from urllib.parse import urlparse
            parsed_url = urlparse(self.pg_url)
            
            # Formato esperado: postgresql://usuario:contraseña@host:puerto/basededatos
            username = parsed_url.username
            password = parsed_url.password
            host = parsed_url.hostname
            port = parsed_url.port or 5432
            dbname = parsed_url.path.lstrip('/')
            
            # Añadir parámetros específicos de Neon para mejor conectividad
            connect_params = {
                'user': username,
                'password': password,
                'host': host,
                'port': port,
                'dbname': dbname,
                'connect_timeout': 15,  # Aumentar timeout
                'sslmode': 'require',   # Requerido por Neon
                'application_name': 'AM3.1_backup_tool',
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
            
            logger.info(f"Conectando a PostgreSQL en {host}:{port}/{dbname} como {username}")
            return psycopg2.connect(**connect_params)
            
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise
    
    def _connect_sqlite(self):
        """Establecer conexión a SQLite."""
        try:
            # Asegurar que el directorio existe
            self.sqlite_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Conectar con parámetros optimizados
            conn = sqlite3.connect(str(self.sqlite_path), timeout=60.0)
            
            # Configurar para mejor rendimiento
            conn.execute("PRAGMA synchronous = OFF")
            conn.execute("PRAGMA journal_mode = MEMORY")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA cache_size = 10000")
            
            return conn
        except Exception as e:
            logger.error(f"Error conectando a SQLite: {e}")
            raise
    
    def _backup_sqlite(self):
        """Crear copia de seguridad de SQLite."""
        if not self.sqlite_path.exists():
            return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"app_db_backup_{timestamp}.db"
        
        shutil.copy2(self.sqlite_path, backup_path)
        logger.info(f"Backup creado en: {backup_path}")
        return backup_path
    
    def _get_postgres_tables(self, pg_conn):
        """Obtener lista de tablas en PostgreSQL."""
        cursor = pg_conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def _get_table_columns(self, pg_conn, table_name):
        """Obtener columnas de una tabla en PostgreSQL."""
        cursor = pg_conn.cursor()
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [(row[0], row[1]) for row in cursor.fetchall()]
        cursor.close()
        return columns
    
    def _create_sqlite_table(self, sqlite_conn, table_name, columns):
        """Crear tabla en SQLite basada en estructura de PostgreSQL."""
        # Mapeo de tipos PostgreSQL a SQLite
        type_map = {
            'integer': 'INTEGER',
            'bigint': 'INTEGER',
            'smallint': 'INTEGER',
            'character varying': 'TEXT',
            'varchar': 'TEXT',
            'text': 'TEXT',
            'boolean': 'INTEGER',  # SQLite no tiene boolean
            'timestamp without time zone': 'TEXT',
            'timestamp with time zone': 'TEXT',
            'date': 'TEXT',
            'time': 'TEXT',
            'numeric': 'REAL',
            'double precision': 'REAL',
            'real': 'REAL',
            'json': 'TEXT',
            'jsonb': 'TEXT',
            'float': 'REAL'
        }
        
        # Generar definición de columnas
        column_defs = []
        for col_name, col_type in columns:
            # Buscar el tipo en el mapa o usar TEXT por defecto
            sqlite_type = type_map.get(col_type.lower(), 'TEXT')
            column_defs.append(f'"{col_name}" {sqlite_type}')
        
        # Crear sentencia SQL para crear tabla
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {', '.join(column_defs)}
        );
        """
        
        cursor = sqlite_conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS \"{table_name}\"")
        cursor.execute(create_sql)
        sqlite_conn.commit()
        cursor.close()
    
    def download_postgres_to_sqlite(self):
        """
        Transferir datos de PostgreSQL a SQLite mediante SQL directo.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        backup_path = None
        pg_conn = None
        sqlite_conn = None
        
        try:
            logger.info(f"Iniciando transferencia de PostgreSQL a SQLite: {self.sqlite_path}")
            logger.info("URL de conexión de PostgreSQL: [OCULTO POR SEGURIDAD]")
            
            # Backup de SQLite si existe
            if self.sqlite_path.exists():
                backup_path = self._backup_sqlite()
                logger.info(f"Backup de SQLite creado en: {backup_path}")
                
            # Intentar conexión a PostgreSQL con reintentos
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    logger.info(f"Intento de conexión a PostgreSQL {retry_count + 1}/{max_retries}")
                    pg_conn = self._connect_postgres()
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    logger.warning(f"Error de conexión a PostgreSQL: {e}. Reintentando...")
                    time.sleep(2 ** retry_count)  # Backoff exponencial
            
            # Intentar conexión a SQLite
            sqlite_conn = self._connect_sqlite()
            
            # Configurar SQLite para mejor rendimiento
            sqlite_conn.execute("PRAGMA synchronous = OFF")
            sqlite_conn.execute("PRAGMA journal_mode = MEMORY")
            sqlite_conn.execute("PRAGMA temp_store = MEMORY")
            
            # Obtener lista de tablas
            tables = self._get_postgres_tables(pg_conn)
            logger.info(f"Encontradas {len(tables)} tablas en PostgreSQL")
            
            # Para cada tabla, transferir datos
            processed_tables = 0
            total_tables = len(tables)
            total_rows = 0
            
            for table_name in tables:
                processed_tables += 1
                logger.info(f"Procesando tabla {processed_tables}/{total_tables}: {table_name}")
                
                # Obtener columnas
                columns = self._get_table_columns(pg_conn, table_name)
                col_names = [col[0] for col in columns]
                
                # Crear tabla en SQLite
                self._create_sqlite_table(sqlite_conn, table_name, columns)
                
                # Obtener datos de PostgreSQL
                pg_cursor = pg_conn.cursor()
                pg_cursor.execute(f"SELECT * FROM \"{table_name}\"")
                rows = pg_cursor.fetchall()
                pg_cursor.close()
                
                if rows:
                    logger.info(f"Transfiriendo {len(rows)} filas para tabla {table_name}")
                    total_rows += len(rows)
                    
                    # Generar placeholders para INSERT
                    placeholders = ", ".join(["?" for _ in range(len(col_names))])
                    
                    # Insertar datos en SQLite
                    sqlite_cursor = sqlite_conn.cursor()
                    
                    try:
                        # Usar placeholders para valores
                        insert_sql = f"INSERT INTO \"{table_name}\" ({', '.join([f'\"{col}\"' for col in col_names])}) VALUES ({placeholders})"
                        
                        # Insertar en lotes para mejor rendimiento
                        batch_size = 100
                        for i in range(0, len(rows), batch_size):
                            batch = rows[i:i+batch_size]
                            sqlite_cursor.executemany(insert_sql, batch)
                        
                        sqlite_conn.commit()
                    except sqlite3.Error as e:
                        logger.warning(f"Error insertando datos en tabla {table_name}: {e}")
                        # Continuar con la siguiente tabla
                        sqlite_conn.rollback()
                        continue
                    finally:
                        sqlite_cursor.close()
            
            sqlite_conn.execute("PRAGMA optimize")
            logger.info(f"Transferencia completada. {processed_tables} tablas y {total_rows} filas transferidas.")
            return True, f"Base de datos descargada exitosamente. {processed_tables} tablas y {total_rows} filas transferidas."
            
        except Exception as e:
            logger.exception(f"Error durante la transferencia: {e}")
            
            # Restaurar backup si hay error
            if backup_path and backup_path.exists():
                try:
                    if sqlite_conn:
                        sqlite_conn.close()
                    
                    shutil.copy2(backup_path, self.sqlite_path)
                    logger.info(f"Restaurado backup desde: {backup_path}")
                except Exception as restore_e:
                    logger.error(f"Error al restaurar backup: {restore_e}")
            
            return False, f"Error al descargar base de datos: {str(e)}"
        
        finally:
            # Cerrar conexiones
            if pg_conn:
                pg_conn.close()
            if sqlite_conn:
                sqlite_conn.close()

    def upload_sqlite_to_postgres(self):
        """
        Transferir datos de SQLite a PostgreSQL mediante SQL directo.
        
        Returns:
            tuple: (éxito, mensaje)
        """
        pg_conn = None
        sqlite_conn = None
        
        try:
            logger.info("Iniciando transferencia de SQLite a PostgreSQL")
            
            # Verificar que existe la base de datos local
            if not self.sqlite_path.exists():
                return False, f"No se encontró la base de datos local en {self.sqlite_path}"
            
            # Conectar a ambas bases de datos
            pg_conn = self._connect_postgres()
            sqlite_conn = self._connect_sqlite()
            
            # Obtener lista de tablas en SQLite
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in sqlite_cursor.fetchall()]
            sqlite_cursor.close()
            
            logger.info(f"Encontradas {len(tables)} tablas en SQLite")
            
            # Para cada tabla, transferir datos
            processed_tables = 0
            total_tables = len(tables)
            total_rows = 0
            
            for table_name in tables:
                processed_tables += 1
                logger.info(f"Procesando tabla {processed_tables}/{total_tables}: {table_name}")
                
                # Obtener columnas de la tabla en SQLite
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
                columns = [row[1] for row in sqlite_cursor.fetchall()]
                
                # Obtener datos de SQLite
                sqlite_cursor.execute(f"SELECT * FROM \"{table_name}\"")
                rows = sqlite_cursor.fetchall()
                sqlite_cursor.close()
                
                if rows:
                    logger.info(f"Transfiriendo {len(rows)} filas para tabla {table_name}")
                    total_rows += len(rows)
                    
                    # Eliminar datos existentes en PostgreSQL
                    pg_cursor = pg_conn.cursor()
                    pg_cursor.execute(f"DELETE FROM \"{table_name}\"")
                    
                    # Generar placeholders para INSERT
                    placeholders = ", ".join(["%s" for _ in range(len(columns))])
                    
                    # Insertar datos en PostgreSQL
                    try:
                        insert_sql = f"INSERT INTO \"{table_name}\" ({', '.join([f'\"{col}\"' for col in columns])}) VALUES ({placeholders})"
                        
                        # Insertar en lotes para mejor rendimiento
                        batch_size = 100
                        for i in range(0, len(rows), batch_size):
                            batch = rows[i:i+batch_size]
                            pg_cursor.executemany(insert_sql, batch)
                        
                        pg_conn.commit()
                    except psycopg2.Error as e:
                        logger.warning(f"Error insertando datos en tabla {table_name}: {e}")
                        # Continuar con la siguiente tabla
                        pg_conn.rollback()
                        continue
                    finally:
                        pg_cursor.close()
            
            logger.info(f"Transferencia completada. {processed_tables} tablas y {total_rows} filas transferidas.")
            return True, f"Base de datos subida exitosamente. {processed_tables} tablas y {total_rows} filas transferidas."
            
        except Exception as e:
            logger.exception(f"Error durante la transferencia: {e}")
            return False, f"Error al subir base de datos: {str(e)}"
        
        finally:
            # Cerrar conexiones
            if pg_conn:
                pg_conn.close()
            if sqlite_conn:
                sqlite_conn.close()

# Función auxiliar para obtener instancia configurada
def get_direct_transfer(app=None):
    """
    Crear instancia configurada para transferencia directa.
    
    Args:
        app: Aplicación Flask (opcional)
    
    Returns:
        DirectDatabaseTransfer: Instancia configurada
    """
    if app:
        pg_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        sqlite_path = app.config.get('DB_PATH')
    else:
        # Valores por defecto si no hay app
        import os
        from pathlib import Path
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        pg_url = os.environ.get('DATABASE_URL')
        sqlite_path = os.environ.get('DB_PATH') or str(base_dir / 'instance' / 'app.db')
    
    return DirectDatabaseTransfer(pg_url, sqlite_path)
