@echo off
echo Restaurando la carga de proveedores en hoja_trabajo_routes.py...

powershell -Command "(Get-Content 'app\routes\hoja_trabajo_routes.py') -replace '    # Obtener todos los proveedores asignados a partidas \(versi\u00f3n temporal sin campos unitario/cantidad\)\n    proveedores_por_partida = \{\}', '    # Obtener todos los proveedores asignados a partidas\n    proveedores_por_partida = {}\n    for partida in hoja.partidas:\n        proveedores_por_partida[partida.id] = db.session.query(ProveedorPartida).filter_by(id_partida=partida.id).all()' | Set-Content 'app\routes\hoja_trabajo_routes.py'"

echo.
echo Proceso completado. Ahora debe reiniciar la aplicacion.
echo Presione cualquier tecla para salir...
pause > nul
