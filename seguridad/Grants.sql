-- Usar el catálogo
USE CATALOG catalog_prod;

-- Permisos en el catálogo
GRANT USAGE ON CATALOG catalog_prod
TO bi_power_users;

-- Permisos en el schema
GRANT USAGE ON SCHEMA catalog_prod.golden
TO bi_power_users;

-- Permisos en todas las tablas del schema
GRANT SELECT ON SCHEMA catalog_prod.golden
TO bi_power_users;

-- Verificar permisos
SHOW GRANTS ON CATALOG catalog_prod;
SHOW GRANTS ON SCHEMA catalog_prod.golden;