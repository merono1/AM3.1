-- Migración PostgreSQL para añadir columnas unitario y cantidad a proveedores_partidas

-- Verificar si ya existen las columnas
DO $$ 
DECLARE
    unitario_exists BOOLEAN;
    cantidad_exists BOOLEAN;
BEGIN
    -- Comprobar si la columna unitario existe
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'proveedores_partidas' AND column_name = 'unitario'
    ) INTO unitario_exists;

    -- Comprobar si la columna cantidad existe
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'proveedores_partidas' AND column_name = 'cantidad'
    ) INTO cantidad_exists;

    -- Añadir columna unitario si no existe
    IF NOT unitario_exists THEN
        ALTER TABLE proveedores_partidas ADD COLUMN unitario VARCHAR(10);
        RAISE NOTICE 'Columna unitario añadida';
    ELSE
        RAISE NOTICE 'Columna unitario ya existe';
    END IF;

    -- Añadir columna cantidad si no existe
    IF NOT cantidad_exists THEN
        ALTER TABLE proveedores_partidas ADD COLUMN cantidad FLOAT DEFAULT 1;
        RAISE NOTICE 'Columna cantidad añadida';
    ELSE
        RAISE NOTICE 'Columna cantidad ya existe';
    END IF;
END $$;

-- Actualizar los valores por defecto
UPDATE proveedores_partidas SET unitario = 'UD' WHERE unitario IS NULL;
UPDATE proveedores_partidas SET cantidad = 1 WHERE cantidad IS NULL;

-- Mostrar las columnas actuales de la tabla
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'proveedores_partidas' 
ORDER BY ordinal_position;
