-- Databricks notebook source
-- MAGIC %python
-- MAGIC dbutils.widgets.removeAll()

-- COMMAND ----------

create widget text storage default "abfss://coffeeshop@adlsdevluis25.dfs.core.windows.net";
create widget text catalogo default "catalog_prod";

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Creacion de catalog

-- COMMAND ----------

CREATE CATALOG IF NOT EXISTS catalog_prod;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Creacion de Schemas

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS catalog_prod.bronze;
CREATE SCHEMA IF NOT EXISTS catalog_prod.silver;
CREATE SCHEMA IF NOT EXISTS catalog_prod.golden;

-- COMMAND ----------

use catalog ${catalogo}

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Creacion tablas Bronze

-- COMMAND ----------

-- Tabla principal de ventas crudas
CREATE OR REPLACE TABLE catalog_prod.bronze.VENTA_CAFE (
  hour_of_day INT,
  cash_type STRING,
  money DOUBLE,
  coffee_name STRING,
  Time_of_Day STRING,
  Weekday STRING,
  Month_name STRING,
  Weekdaysort INT,
  Monthsort INT,
  Date DATE,
  Time STRING,
  ingesta_date TIMESTAMP
)
USING DELTA
LOCATION '${storage}/bronze/VENTA_CAFE'
COMMENT 'Tabla principal - Datos crudos de ventas de café';


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Creacion tablas Silver

-- COMMAND ----------

-- Dimensión: Productos (Cafés)
CREATE OR REPLACE TABLE catalog_prod.silver.DIM_CAFE (
  id_cafe INT NOT NULL,
  coffee_name STRING NOT NULL,
  categoria STRING,
  tamanio STRING,
  precio_base DOUBLE,
  activo BOOLEAN,
  fecha_vigencia DATE,
  PRIMARY KEY (id_cafe)
)
USING DELTA
LOCATION '${storage}/silver/DIM_CAFE'
COMMENT 'Dimensión de productos de café con categorías y precios';

-- Dimensión: Métodos de Pago
CREATE OR REPLACE TABLE catalog_prod.silver.DIM_PAGO (
  id_pago INT NOT NULL,
  cash_type STRING NOT NULL,
  proveedor STRING,
  activo BOOLEAN,
  PRIMARY KEY (id_pago)
)
USING DELTA
LOCATION '${storage}/silver/DIM_PAGO'
COMMENT 'Dimensión de métodos de pago';

-- Dimensión: Calendario
CREATE OR REPLACE TABLE catalog_prod.silver.DIM_FECHA (
  fecha DATE NOT NULL,
  anio INT NOT NULL,
  trimestre INT NOT NULL,
  mes INT NOT NULL,
  Month_name STRING NOT NULL,
  Monthsort INT NOT NULL,
  dia_semana INT NOT NULL,
  Weekday STRING NOT NULL,
  Weekdaysort INT NOT NULL,
  dia_del_mes INT NOT NULL,
  es_fin_semana BOOLEAN,
  es_feriado BOOLEAN,
  PRIMARY KEY (fecha)
)
USING DELTA
LOCATION '${storage}/silver/DIM_FECHA'
COMMENT 'Dimensión calendario para análisis temporal';

-- Tabla de hechos: Ventas limpias
CREATE OR REPLACE TABLE catalog_prod.silver.HECHO_VENTAS (
  fecha DATE NOT NULL,
  hora TIMESTAMP NOT NULL,
  id_cafe INT NOT NULL,
  id_pago INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DOUBLE NOT NULL,
  monto_total DOUBLE NOT NULL,
  franja_horaria STRING,
  fecha_procesamiento TIMESTAMP
)
USING DELTA
LOCATION '${storage}/silver/HECHO_VENTAS'
COMMENT 'Tabla de hechos con transacciones de venta limpias y conformadas';


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Creacion tablas Golden

-- COMMAND ----------

-- Análisis: Ventas Diarias
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_VENTAS_DIARIAS (
  fecha DATE NOT NULL,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  ticket_promedio DOUBLE,
  cantidad_total_vendida BIGINT,
  productos_unicos_vendidos BIGINT,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (fecha)
)
USING DELTA
LOCATION '${storage}/gold/AGG_VENTAS_DIARIAS'
COMMENT 'Métricas diarias de rendimiento de ventas';

-- Análisis: Ventas por Producto
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_VENTAS_POR_CAFE (
  id_cafe INT NOT NULL,
  coffee_name STRING NOT NULL,
  categoria STRING,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  cantidad_total_vendida BIGINT,
  ticket_promedio DOUBLE,
  ranking_ingresos BIGINT,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (id_cafe)
)
USING DELTA
LOCATION '${storage}/gold/AGG_VENTAS_POR_CAFE'
COMMENT 'Rendimiento de ventas y ranking por producto';

-- Análisis: Ventas por Método de Pago
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_VENTAS_POR_PAGO (
  cash_type STRING NOT NULL,
  proveedor STRING,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  ticket_promedio DOUBLE,
  participacion_pct DOUBLE,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (cash_type, proveedor)
)
USING DELTA
LOCATION '${storage}/gold/AGG_VENTAS_POR_PAGO'
COMMENT 'Rendimiento y distribución por método de pago';

-- Análisis: Ventas por Día de la Semana
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_VENTAS_POR_DIA_SEMANA (
  Weekday STRING NOT NULL,
  Weekdaysort INT NOT NULL,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  ticket_promedio DOUBLE,
  ingreso_promedio_diario DOUBLE,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (Weekday)
)
USING DELTA
LOCATION '${storage}/gold/AGG_VENTAS_POR_DIA_SEMANA'
COMMENT 'Análisis de patrones de venta semanales';

-- Análisis: Ventas por Franja Horaria
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_VENTAS_POR_FRANJA_HORARIA (
  franja_horaria STRING NOT NULL,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  ticket_promedio DOUBLE,
  hora_pico INT,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (franja_horaria)
)
USING DELTA
LOCATION '${storage}/gold/AGG_VENTAS_POR_FRANJA_HORARIA'
COMMENT 'Análisis de patrones de venta por hora del día';

-- Análisis: Top Productos por Período
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_TOP_PRODUCTOS (
  periodo_analisis STRING NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  id_cafe INT NOT NULL,
  coffee_name STRING NOT NULL,
  categoria STRING,
  ingresos_totales DOUBLE,
  cantidad_total BIGINT,
  ranking_producto BIGINT,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (periodo_analisis, fecha_inicio, id_cafe)
)
USING DELTA
LOCATION '${storage}/gold/AGG_TOP_PRODUCTOS'
COMMENT 'Productos con mejor rendimiento por diferentes períodos de tiempo';

-- Análisis: Resumen Ejecutivo Mensual
CREATE OR REPLACE TABLE catalog_prod.golden.AGG_RESUMEN_MENSUAL (
  anio INT NOT NULL,
  mes INT NOT NULL,
  Month_name STRING NOT NULL,
  ingresos_totales DOUBLE,
  total_transacciones BIGINT,
  ticket_promedio DOUBLE,
  cafe_mas_vendido STRING,
  metodo_pago_principal STRING,
  dia_semana_mas_fuerte STRING,
  ultima_actualizacion TIMESTAMP,
  PRIMARY KEY (anio, mes)
)
USING DELTA
LOCATION '${storage}/gold/AGG_RESUMEN_MENSUAL'
COMMENT 'Resumen ejecutivo mensual con KPIs principales';