# Solución Error "no such column: presupuestos.estado_workflow"

La solución implementada recrea la base de datos incluyendo directamente la columna estado_workflow.

## Archivos creados:
- reset_and_fix_db.py: script para recrear la base de datos
- reset_database.bat: ejecutable para simplificar el proceso

## Cómo usar:
1. Ejecutar reset_database.bat
2. Reiniciar la aplicación con python run.py

## Nota: 
Esta solución elimina todos los datos existentes pero garantiza que la estructura sea correcta.