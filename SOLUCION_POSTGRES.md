# Solución para migración de PostgreSQL

## Problema detectado

Se ha encontrado un error al acceder a las hojas de trabajo después de implementar los campos `unitario` y `cantidad` en el modelo `ProveedorPartida`. El error indica que estas columnas no existen en la base de datos PostgreSQL:

```
Error de programación
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) columna proveedores_partidas.unitario no existe
```

## Causa del problema

Hemos añadido nuevos campos al modelo `ProveedorPartida` en el código de la aplicación, pero no hemos migrado estas columnas a la base de datos PostgreSQL. El sistema está intentando acceder a estas columnas que no existen todavía.

## Pasos para solucionar el problema

1. **Aplicar la solución temporal**:
   - La aplicación ahora tiene una versión temporal que no intenta acceder a las nuevas columnas
   - Hemos creado una versión especial de la plantilla `editar_hoja_multiprov.html` que no requiere estos campos

2. **Ejecutar la migración para PostgreSQL**:
   ```
   migrar_postgres.bat
   ```
   Esto añadirá las columnas `unitario` y `cantidad` a la tabla `proveedores_partidas` en PostgreSQL.

3. **Revertir a la versión normal**:
   - Una vez completada la migración, modificar de nuevo el archivo `hoja_trabajo_routes.py` para restaurar la consulta de proveedores:

   ```python
   # Obtener todos los proveedores asignados a partidas
   proveedores_por_partida = {}
   for partida in hoja.partidas:
       proveedores_por_partida[partida.id] = db.session.query(ProveedorPartida).filter_by(id_partida=partida.id).all()
   ```

4. **Reiniciar la aplicación** para que se carguen los cambios.

## Notas importantes

- La migración de PostgreSQL es específica para bases de datos PostgreSQL.
- Si también se utiliza SQLite, es necesario ejecutar `migrar_proveedores_partidas.bat` para esa base de datos.
- Los campos ahora ocultos en la interfaz funcionarán correctamente después de la migración.
- El error no afecta a la funcionalidad principal, solo a la visualización de proveedores asociados a partidas.

## Verificación

Para comprobar que la migración se ha realizado correctamente, ejecutar una consulta SQL para ver las columnas de la tabla:

```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'proveedores_partidas';
```

Deberían aparecer las columnas `unitario` y `cantidad` en el resultado.
