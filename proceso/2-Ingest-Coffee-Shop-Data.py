# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ### Definición de Parámetros

# COMMAND ----------

# Definición de constantes
ruta = "abfss://coffeeshop@adlsdevluis25.dfs.core.windows.net/raw/coffe.csv"
catalogo = "catalog_dev"
esquema = "bronze"
tabla = "VENTA_CAFE"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Definición del Schema

# COMMAND ----------

# Schema para los datos de ventas de café
coffee_schema = StructType(fields=[
    StructField("hour_of_day", IntegerType(), True),
    StructField("cash_type", StringType(), True),
    StructField("money", DoubleType(), True),
    StructField("coffee_name", StringType(), True),
    StructField("Time_of_Day", StringType(), True),
    StructField("Weekday", StringType(), True),
    StructField("Month_name", StringType(), True),
    StructField("Weekdaysort", IntegerType(), True),
    StructField("Monthsort", IntegerType(), True),
    StructField("Date", StringType(), True),
    StructField("Time", StringType(), True)
])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Lectura de Datos Crudos

# COMMAND ----------

# Lectura del CSV con schema definido
df_coffee = spark.read\
    .option('header', True)\
    .schema(coffee_schema)\
    .csv(ruta)

# COMMAND ----------

# Convertir Date de string a date real con formato dd/MM/yyyy

df_coffee = df_coffee.withColumn("Date", to_date("Date", "dd/MM/yyyy"))


# COMMAND ----------

# MAGIC %md
# MAGIC ### Agregar Metadatos de Ingesta

# COMMAND ----------

# Agregar solo timestamp de ingesta
df_coffee_bronze = df_coffee.withColumn("ingesta_date", current_timestamp())

# COMMAND ----------

# Escribir en tabla Bronze (modo overwrite)
df_coffee_bronze.write\
    .mode("overwrite")\
    .saveAsTable(f"{catalogo}.{esquema}.{tabla}")

