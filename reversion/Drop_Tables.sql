-- =========================
-- 1. Eliminar tablas Bronze
-- =========================
DROP TABLE IF EXISTS catalog_prod.bronze.VENTA_CAFE;

-- =========================
-- 2. Eliminar tablas Silver
-- =========================
DROP TABLE IF EXISTS catalog_prod.silver.DIM_CAFE;
DROP TABLE IF EXISTS catalog_prod.silver.DIM_PAGO;
DROP TABLE IF EXISTS catalog_prod.silver.DIM_FECHA;
DROP TABLE IF EXISTS catalog_prod.silver.HECHO_VENTAS;

-- =========================
-- 3. Eliminar tablas Golden
-- =========================
DROP TABLE IF EXISTS catalog_prod.golden.AGG_VENTAS_DIARIAS;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_VENTAS_POR_CAFE;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_VENTAS_POR_PAGO;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_VENTAS_POR_DIA_SEMANA;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_VENTAS_POR_FRANJA_HORARIA;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_TOP_PRODUCTOS;
DROP TABLE IF EXISTS catalog_prod.golden.AGG_RESUMEN_MENSUAL;

-- =========================
-- 4. Eliminar esquemas
-- =========================
DROP SCHEMA IF EXISTS catalog_prod.bronze CASCADE;
DROP SCHEMA IF EXISTS catalog_prod.silver CASCADE;
DROP SCHEMA IF EXISTS catalog_prod.golden CASCADE;

-- =========================
-- 5. Eliminar catálogo
-- =========================
DROP CATALOG IF EXISTS catalog_prod CASCADE;
