-- Databricks notebook source
-- MAGIC %python
-- MAGIC dbutils.widgets.removeAll()

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.widgets.text("storage","abfss://lhcldata@adlssmartdata1504.dfs.core.windows.net")
-- MAGIC dbutils.widgets.text("catalogo","catalog_dev")

-- COMMAND ----------

-- MAGIC %python
-- MAGIC ruta = dbutils.widgets.get("storage")

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Eliminacion tablas Bronze

-- COMMAND ----------

-- DROP TABLES
DROP TABLE IF EXISTS catalog_dev.bronze.VENTA_CAFE;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC ## REMOVE DATA (Bronze)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/CLIENTES", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/VENTAS", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/PRODUCTOS", True)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Eliminacion tablas Silver

-- COMMAND ----------

-- DROP TABLES
DROP TABLE IF EXISTS catalog_dev.silver.VENTAS_LIMPIAS;
DROP TABLE IF EXISTS catalog_dev.silver.CLIENTES_VALIDOS;
DROP TABLE IF EXISTS catalog_dev.silver.DETALLE_PRODUCTOS;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # REMOVE DATA (Silver)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/VENTAS_LIMPIAS", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/CLIENTES_VALIDOS", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/DETALLE_PRODUCTOS", True)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Eliminacion tablas Golden

-- COMMAND ----------

-- DROP TABLES
DROP TABLE IF EXISTS catalog_dev.golden.KPIS_VENTAS;
DROP TABLE IF EXISTS catalog_dev.golden.SEGMENTOS_CLIENTES;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # REMOVE DATA (Golden)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/KPIS_VENTAS", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/SEGMENTOS_CLIENTES", True)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Eliminacion tablas Exploratory

-- COMMAND ----------

-- DROP TABLES
DROP TABLE IF EXISTS catalog_dev.exploratory.EXPERIMENTOS;
DROP TABLE IF EXISTS catalog_dev.exploratory.PRUEBAS_MODELOS_EXT;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # REMOVE DATA (Exploratory)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/EXPERIMENTOS", True)
-- MAGIC dbutils.fs.rm(f"{ruta}/tablas/PRUEBAS_MODELOS_EXT", True)