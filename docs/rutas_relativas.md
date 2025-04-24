# Configuración de rutas relativas en AM3.1

Este documento explica cómo se ha implementado un sistema de rutas relativas en la aplicación AM3.1 para facilitar su uso en diferentes equipos sin necesidad de modificar el código.

## Funcionamiento

La aplicación ahora utiliza un sistema centralizado de configuración que:

1. Detecta automáticamente la ubicación de la aplicación
2. Utiliza rutas relativas para todos los recursos
3. Permite configurar rutas específicas por medio del archivo `.env`

## Archivos principales

- `config.py`: Contiene todas las definiciones de rutas y configuraciones
- `main.py`: Utiliza la configuración centralizada
- `.env`: Contiene variables personalizables para cada equipo

## Personalización por equipo

Para usar la aplicación en un nuevo equipo, simplemente copia el archivo `.env.example` a `.env` y ajusta las siguientes variables:

```
# Ruta de la base de datos SQLite (se usa si DATABASE_URL no está definido)
DB_PATH=app/data/app.db

# Directorios personalizados (ajustar según cada equipo)
CLIENTES_DIR=C:/Users/TuUsuario/Documents/Clientes
LOGO_PATH=app/static/img/logo.jpg
```

Donde:
- `CLIENTES_DIR`: Es la ruta donde se guardarán los datos de clientes
- `LOGO_PATH`: Es la ruta al logo de la aplicación

## Adaptando el código existente

Si necesitas crear o modificar código que trabaje con rutas, sigue estas pautas:

### Importar funciones y variables de config.py

```python
from config import (
    BASE_DIR,              # Directorio base de la aplicación
    CONFIG,                # Diccionario con configuraciones específicas
    get_abs_path,          # Función para obtener rutas absolutas
    ensure_dirs_exist      # Función para crear directorios
)
```

### Usar rutas relativas

```python
# En lugar de:
ruta_archivo = "C:/Users/Usuario/Desktop/AM3.1/app/data/archivo.txt"

# Usar:
ruta_archivo = get_abs_path("app/data/archivo.txt")
```

### Usar directorios configurables

```python
# En lugar de:
ruta_cliente = os.path.join("C:/Clientes", nombre_cliente)

# Usar:
ruta_cliente = os.path.join(CONFIG['clientes_dir'], nombre_cliente)
```

## Ventajas

1. **Portabilidad**: La aplicación funciona sin cambios en cualquier equipo
2. **Mantenimiento**: Facilita el trabajo en equipo y el control de versiones
3. **Adaptabilidad**: Cada usuario puede configurar rutas según su sistema sin tocar el código
4. **Robustez**: Los directorios necesarios se crean automáticamente

## Recomendaciones

- Nunca uses rutas absolutas codificadas directamente en el código
- Si necesitas una nueva ruta configurable, añádela a `CONFIG` en `config.py`
- Para nuevos módulos, importa siempre las configuraciones necesarias desde `config.py`
