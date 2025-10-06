-- Databricks notebook source
GRANT USE CATALOG ON CATALOG demo_catalog TO `Dvelopers`;
GRANT USE CATALOG ON CATALOG demo_catalog TO `Admins`;

-- COMMAND ----------

GRANT USE SCHEMA ON SCHEMA catalog_dev.bronze TO `Dvelopers`;
GRANT CREATE ON SCHEMA catalog_dev.bronze TO `Dvelopers`;

-- COMMAND ----------

GRANT SELECT ON TABLE demo_catalog.ventas_2025.clientes_ext TO `Dvelopers`;
GRANT SELECT ON TABLE demo_catalog.ventas_2025.equipos_ext TO `Dvelopers`;

-- GRANT CREATE ON CATALOG demo_catalog TO `Dvelopers`;
-- GRANT SELECT ON CATALOG demo_catalog TO `Dvelopers`;
-- GRANT ALL PRIVILEGES ON CATALOG demo_catalog TO `Admins`;