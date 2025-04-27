"""
Servicio para operaciones de base de datos.
Este módulo provee funciones genéricas para realizar operaciones CRUD en la base de datos.
"""

from app import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging
import time
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para aplicar optimizaciones SQLite cuando se inicia la aplicación
def setup_db_optimizations(app):
    """Configura optimizaciones para la base de datos SQLite cuando la aplicación está lista"""
    try:
        # Configurar pragmas para mejorar rendimiento
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous=NORMAL")  # Menos escrituras a disco (pero aún seguro)
            cursor.execute("PRAGMA cache_size=5000")  # Más cache en memoria (5MB)
            cursor.execute("PRAGMA temp_store=MEMORY")  # Almacenar tablas temporales en memoria
            cursor.execute("PRAGMA foreign_keys=ON")  # Garantizar integridad referencial
            cursor.close()
        
        logger.info("Optimizaciones para SQLite configuradas correctamente")
    except Exception as e:
        logger.warning(f"No se pudieron aplicar optimizaciones para SQLite: {str(e)}")

# Mantener una caché simple para consultas frecuentes
_query_cache = {}

def clear_cache():
    """Limpia la caché de consultas"""
    global _query_cache
    _query_cache = {}

# Función para ejecutar consultas con reintentos
def execute_with_retry(query_func, max_retries=5, retry_delay=0.2):
    """
    Ejecuta una función de consulta con reintentos automáticos en caso de errores de conexión
    
    Args:
        query_func: Función que ejecuta la consulta a la base de datos
        max_retries: Número máximo de reintentos
        retry_delay: Retraso inicial entre reintentos (se incrementa exponencialmente)
        
    Returns:
        El resultado de la consulta
    """
    retries = 0
    last_error = None
    
    # Lista de errores de conexión para SQLite
    connection_errors = [
        "database is locked",
        "disk i/o error",
        "unable to open database file",
        "no such table",
        "disk full",
        "database or disk is full",
        "database schema has changed",
        "database disk image is malformed"
    ]
    
    while retries < max_retries:
        try:
            return query_func()
        except SQLAlchemyError as e:
            last_error = e
            error_str = str(e).lower()
            
            # Verificar si alguno de los errores de conexión está presente
            is_connection_error = False
            for error_msg in connection_errors:
                if error_msg in error_str:
                    is_connection_error = True
                    break
                    
            if is_connection_error:
                retries += 1
                # Exponential backoff para los reintentos (espera más tiempo en cada reintento)
                wait_time = retry_delay * (2 ** (retries - 1))  # 0.2, 0.4, 0.8, 1.6, 3.2, ...
                logger.warning(f"Error de conexión, reintentando ({retries}/{max_retries}) en {wait_time:.2f}s...")
                time.sleep(wait_time)  # Espera exponencial
                
                # Si es el último intento, intentar un reinicio explícito de la conexión
                if retries == max_retries - 1:
                    logger.warning("Intentando reiniciar la conexión explícitamente...")
                    try:
                        db.session.rollback()
                        db.session.close()
                        # Intentar reconectar explícitamente
                        db.engine.dispose()
                    except Exception as reconnect_error:
                        logger.error(f"Error al reiniciar conexión: {reconnect_error}")
            else:
                # Si no es un error de conexión, no reintentamos
                logger.error(f"Error no relacionado con la conexión: {error_str}")
                break
    
    # Si llegamos aquí, todos los reintentos fallaron
    if last_error:
        logger.error(f"Error después de {max_retries} intentos: {last_error}")
        raise last_error
    
    # Si llegamos aquí sin error pero sin retorno, es un caso inusual
    logger.error("Fallo desconocido en la consulta")
    raise Exception("Fallo desconocido en la consulta")

def get_all(model, order_by=None, use_cache=False):
    """
    Obtiene todos los registros de un modelo específico.
    
    Args:
        model: El modelo de SQLAlchemy
        order_by: Campo opcional para ordenar los resultados
        use_cache: Si es True, intenta usar resultados en caché
        
    Returns:
        Lista de instancias del modelo
    """
    try:
        # Intentar usar caché si está habilitada
        if use_cache:
            cache_key = f"{model.__name__}_{order_by}"
            if cache_key in _query_cache:
                logger.debug(f"Usando caché para {cache_key}")
                return _query_cache[cache_key]
        
        # Realizar la consulta con reintentos automáticos
        def query_func():
            if order_by:
                return model.query.order_by(order_by).all()
            else:
                return model.query.all()
        
        # Ejecutar con reintentos si no es caché
        start_time = time.time()
        if not use_cache:
            result = execute_with_retry(query_func)
        else:
            result = query_func()
        
        # Almacenar en caché si está habilitada
        if use_cache:
            _query_cache[cache_key] = result
            
        # Registrar consultas lentas
        query_time = time.time() - start_time
        if query_time > 0.5:
            logger.warning(f"Consulta get_all({model.__name__}) tardó {query_time:.2f}s")
            
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de {model.__name__}: {str(e)}")
        return []

def get_by_id(model, id, use_cache=False):
    """
    Obtiene un registro por su ID.
    
    Args:
        model: El modelo de SQLAlchemy
        id: El ID del registro a buscar
        use_cache: Si es True, intenta usar resultados en caché
        
    Returns:
        Instancia del modelo o None si no se encuentra
    """
    try:
        # Intentar usar caché si está habilitada
        if use_cache:
            cache_key = f"{model.__name__}_id_{id}"
            if cache_key in _query_cache:
                logger.debug(f"Usando caché para {cache_key}")
                return _query_cache[cache_key]
        
        # Función de consulta con get() para optimizar
        def query_func():
            return model.query.get(id)
        
        # Ejecutar con reintentos si no es caché
        start_time = time.time()
        if not use_cache:
            result = execute_with_retry(query_func)
        else:
            result = query_func()
        
        # Almacenar en caché si está habilitada
        if use_cache and result is not None:
            _query_cache[cache_key] = result
            
        # Registrar consultas lentas
        query_time = time.time() - start_time
        if query_time > 0.2:  # 200ms es lento para una búsqueda por ID
            logger.warning(f"Consulta get_by_id({model.__name__}, {id}) tardó {query_time:.2f}s")
            
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener {model.__name__} con ID {id}: {str(e)}")
        return None

def create(model, data):
    """
    Crea un nuevo registro en la base de datos.
    
    Args:
        model: El modelo de SQLAlchemy
        data: Diccionario con los datos a insertar
        
    Returns:
        La instancia creada si se realizó correctamente, None en caso contrario
    """
    try:
        def query_func():
            instance = model(**data)
            db.session.add(instance)
            db.session.commit()
            return instance
        
        return execute_with_retry(query_func)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al crear {model.__name__}: {str(e)}")
        raise e

def update(model, id, data):
    """
    Actualiza un registro existente.
    
    Args:
        model: El modelo de SQLAlchemy
        id: ID del registro a actualizar
        data: Diccionario con los datos a actualizar
        
    Returns:
        La instancia actualizada si se realizó correctamente, None en caso contrario
    """
    try:
        def query_func():
            instance = get_by_id(model, id)
            if not instance:
                return None
                
            for key, value in data.items():
                setattr(instance, key, value)
                
            db.session.commit()
            return instance
        
        return execute_with_retry(query_func)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al actualizar {model.__name__} con ID {id}: {str(e)}")
        raise e

def delete(model, id):
    """
    Elimina un registro de la base de datos.
    
    Args:
        model: El modelo de SQLAlchemy
        id: ID del registro a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        def query_func():
            instance = get_by_id(model, id)
            if not instance:
                return False
                
            db.session.delete(instance)
            db.session.commit()
            return True
        
        return execute_with_retry(query_func)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al eliminar {model.__name__} con ID {id}: {str(e)}")
        raise e

def get_filtered(model, **filters):
    """
    Obtiene registros filtrados por los criterios proporcionados.
    
    Args:
        model: El modelo de SQLAlchemy
        **filters: Filtros a aplicar (campo=valor)
        
    Returns:
        Lista de instancias del modelo que cumplen los filtros
    """
    try:
        def query_func():
            query = model.query
            for attr, value in filters.items():
                if hasattr(model, attr):
                    query = query.filter(getattr(model, attr) == value)
            return query.all()
        
        return execute_with_retry(query_func)
    except SQLAlchemyError as e:
        logger.error(f"Error al filtrar {model.__name__}: {str(e)}")
        return []

def get_paginated(model, page=1, per_page=10, order_by=None):
    """
    Obtiene registros paginados.
    
    Args:
        model: El modelo de SQLAlchemy
        page: Número de página (empezando por 1)
        per_page: Número de registros por página
        order_by: Campo opcional para ordenar los resultados
        
    Returns:
        Objeto de paginación de SQLAlchemy
    """
    try:
        def query_func():
            if order_by:
                return model.query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)
            return model.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return execute_with_retry(query_func)
    except SQLAlchemyError as e:
        logger.error(f"Error al paginar {model.__name__}: {str(e)}")
        return None