# app/routes/__init__.py
def register_blueprints(app):
    from app.routes.cliente_routes import clientes_bp
    from app.routes.proyecto_routes import proyectos_bp
    from app.routes.presupuesto_routes import presupuestos_bp
    from app.routes.proveedor_routes import proveedores_bp
    from app.routes.hoja_trabajo_routes import hojas_trabajo_bp
    from app.routes.factura_routes import facturas_bp
    from app.routes.presupuesto_routes_avanzado import register_presupuestos_avanzados
    from app.routes.partida_routes import partidas_bp
    from app.routes.proveedor_partida_routes import proveedor_partida_bp, api_proveedor_partida_bp
    
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proyectos_bp)
    app.register_blueprint(presupuestos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(hojas_trabajo_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(partidas_bp)
    app.register_blueprint(proveedor_partida_bp)
    app.register_blueprint(api_proveedor_partida_bp)
    
    # Registrar rutas avanzadas de presupuestos
    register_presupuestos_avanzados(app)