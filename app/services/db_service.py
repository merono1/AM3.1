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

# Función para aplicar optimizaciones PostgreSQL cuando se inicia la aplicación
def setup_db_optimizations(app):
    """Configura optimizaciones para la base de datos cuando la aplicación está lista"""
    try:
        with app.app_context():
            db_engine_url = str(db.engine.url)
            if 'postgresql' in db_engine_url:
                logger.info("Aplicando optimizaciones para PostgreSQL...")
                
                # Configurar pool de conexiones para PostgreSQL
                @event.listens_for(Engine, "connect")
                def setup_postgresql_connection(dbapi_connection, connection_record):
                    # Desactivar autocommit para mejorar rendimiento
                    if hasattr(dbapi_connection, 'autocommit'):
                        dbapi_connection.autocommit = False
                        
                    # Configurar tiempo de espera para consultas lentas
                    cursor = dbapi_connection.cursor()
                    cursor.execute("SET statement_timeout = 30000;")  # 30 segundos
                    cursor.close()
                
                # Registrar duración de las consultas en modo desarrollo
                if os.environ.get('FLASK_ENV') == 'development':
                    @event.listens_for(Engine, "before_cursor_execute")
                    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                        conn.info.setdefault('query_start_time', []).append(time.time())
                        if len(conn.info['query_start_time']) > 100:  # Evitar fugas de memoria
                            conn.info['query_start_time'] = conn.info['query_start_time'][-100:]
                    
                    @event.listens_for(Engine, "after_cursor_execute")
                    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                        total = time.time() - conn.info['query_start_time'].pop(-1)
                        if total > 0.5:  # Solo registrar consultas lentas (>500ms)
                            logger.warning(f"Consulta lenta ({total:.2f}s): {statement}")
                
                logger.info("Optimizaciones para PostgreSQL aplicadas correctamente")
    except Exception as e:
        logger.warning(f"No se pudieron aplicar optimizaciones para PostgreSQL: {str(e)}")

# Mantener una caché simple para consultas frecuentes
_query_cache = {}

def clear_cache():
    """Limpia la caché de consultas"""
    global _query_cache
    _query_cache = {}

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
        
        # Realizar la consulta
        start_time = time.time()
        if order_by:
            result = model.query.order_by(order_by).all()
        else:
            result = model.query.all()
        
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
        
        # Optimización: Usar get() en lugar de filter_by().first() 
        # ya que get() usa caché de identidad de SQLAlchemy
        start_time = time.time()
        result = model.query.get(id)
        
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
        instance = model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance
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
        instance = get_by_id(model, id)
        if not instance:
            return None
            
        for key, value in data.items():
            setattr(instance, key, value)
            
        db.session.commit()
        return instance
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
        instance = get_by_id(model, id)
        if not instance:
            return False
            
        db.session.delete(instance)
        db.session.commit()
        return True
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
        query = model.query
        for attr, value in filters.items():
            if hasattr(model, attr):
                query = query.filter(getattr(model, attr) == value)
        return query.all()
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
        if order_by:
            return model.query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)
        return model.query.paginate(page=page, per_page=per_page, error_out=False)
    except SQLAlchemyError as e:
        logger.error(f"Error al paginar {model.__name__}: {str(e)}")
        return None