# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transformación Bronze → Silver
# MAGIC Pipeline de limpieza y conformación de datos de ventas de café

# COMMAND ----------

# MAGIC %md
# MAGIC ### Configuración

# COMMAND ----------

catalogo = "catalog_dev"
esquema_origen = "bronze"
esquema_destino = "silver"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Definición de UDFs

# COMMAND ----------

def clasificar_categoria_cafe(nombre_cafe):
    nombre_minuscula = nombre_cafe.lower()
    if any(palabra in nombre_minuscula for palabra in ["espresso","americano with milk", "americano", "cortado"]):
        return "Espresso"
    elif any(palabra in nombre_minuscula for palabra in ["latte", "cappuccino"]):
        return "Latte"
    else:
        return "Otros"

# COMMAND ----------

def clasificar_tamanio_cafe(nombre_cafe):
    nombre_minuscula = nombre_cafe.lower()
    if "americano" in nombre_minuscula or "espresso" in nombre_minuscula:
        return "Grande"
    elif "latte" in nombre_minuscula or "cappuccino" in nombre_minuscula:
        return "Mediano"
    else:
        return "Pequeño"

# COMMAND ----------

def clasificar_rango_precio(precio):
    if precio < 20:
        return "Económico"
    elif 20 <= precio < 32:
        return "Medio"
    else:
        return "Premium"

# COMMAND ----------

categoria_cafe_udf = udf(clasificar_categoria_cafe, StringType())
tamanio_cafe_udf = udf(clasificar_tamanio_cafe, StringType())
rango_precio_udf = udf(clasificar_rango_precio, StringType())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Extracción desde Bronze

# COMMAND ----------

df_ventas = spark.table(f"{catalogo}.{esquema_origen}.VENTA_CAFE")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Limpieza de Datos

# COMMAND ----------

df_ventas_limpio = df_ventas\
    .dropna(how="all")\
    .filter(
        (col("Date").isNotNull()) & 
        (col("coffee_name").isNotNull()) &
        (col("money").isNotNull()) &
        (col("cash_type").isNotNull())
    )\
    .dropDuplicates()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Enriquecimiento de Datos

# COMMAND ----------

df_ventas_enriquecido = df_ventas_limpio\
    .withColumn("categoria_cafe", categoria_cafe_udf(col("coffee_name")))\
    .withColumn("tamanio_cafe", tamanio_cafe_udf(col("coffee_name")))\
    .withColumn("rango_precio", rango_precio_udf(col("money")))\
    .withColumn("marca_tiempo_venta", 
        coalesce(
            to_timestamp(concat(col("Date"), lit(" "), col("Time")), "yyyy-MM-dd HH:mm:ss"),
            to_timestamp(concat(col("Date"), lit(" "), lpad(col("hour_of_day").cast(StringType()), 2, "0"), lit(":"), col("Time")), "yyyy-MM-dd HH:mm:ss.S"),
            to_timestamp(concat(col("Date"), lit(" 00:00:00")))
        )
    )
# COMMAND ----------

# MAGIC %md
# MAGIC ### Construcción Dimensión DIM_CAFE

# COMMAND ----------

df_dim_cafe = df_ventas_enriquecido\
    .groupBy("coffee_name")\
    .agg(
        first("categoria_cafe").alias("categoria_cafe"),
        first("tamanio_cafe").alias("tamanio_cafe"),
        avg("money").alias("precio_base")
    )\
    .withColumn("id_cafe", (monotonically_increasing_id() + 1).cast(IntegerType()))\
    .withColumn("activo", lit(True))\
    .withColumn("fecha_vigencia", current_date())\
    .select(
        "id_cafe", 
        "coffee_name", 
        col("categoria_cafe").alias("categoria"),
        col("tamanio_cafe").alias("tamanio"),
        round(col("precio_base"), 2).alias("precio_base"),
        "activo", 
        "fecha_vigencia"
    )

# COMMAND ----------

df_dim_cafe.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.DIM_CAFE")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Construcción Dimensión DIM_PAGO

# COMMAND ----------

df_dim_pago = df_ventas_enriquecido\
    .select("cash_type")\
    .distinct()\
    .withColumn("id_pago", (monotonically_increasing_id() + 1).cast(IntegerType()))\
    .withColumn("proveedor", 
        when(col("cash_type") == "card", lit("Visa/Mastercard"))
        .when(col("cash_type") == "online", lit("PayPal"))
        .otherwise(lit(None))
    )\
    .withColumn("activo", lit(True))\
    .select("id_pago", "cash_type", "proveedor", "activo")

# COMMAND ----------

df_dim_pago.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.DIM_PAGO")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Construcción Dimensión DIM_FECHA

# COMMAND ----------

df_dim_fecha = df_ventas_enriquecido\
    .select(
        col("Date").alias("fecha"),
        year("Date").alias("anio"),
        quarter("Date").alias("trimestre"),
        month("Date").alias("mes"),
        "Month_name",
        "Monthsort",
        dayofweek("Date").alias("dia_semana"),
        "Weekday",
        "Weekdaysort",
        dayofmonth("Date").alias("dia_del_mes")
    )\
    .distinct()\
    .withColumn("es_fin_semana", col("Weekday").isin("Sat", "Sun"))\
    .withColumn("es_feriado", lit(False))

# COMMAND ----------

df_dim_fecha.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.DIM_FECHA")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Construcción Tabla de Hechos HECHO_VENTAS

# COMMAND ----------

df_consulta_cafe = spark.table(f"{catalogo}.{esquema_destino}.DIM_CAFE")
df_consulta_pago = spark.table(f"{catalogo}.{esquema_destino}.DIM_PAGO")

# COMMAND ----------

df_hecho_ventas = df_ventas_enriquecido.alias("v")\
    .join(
        df_consulta_cafe.alias("c"), 
        col("v.coffee_name") == col("c.coffee_name"), 
        "inner"
    )\
    .join(
        df_consulta_pago.alias("p"), 
        col("v.cash_type") == col("p.cash_type"), 
        "inner"
    )\
    .select(
        col("v.Date").alias("fecha"),
        col("v.marca_tiempo_venta").alias("hora"),
        col("c.id_cafe"),
        col("p.id_pago"),
        lit(1).alias("cantidad"),
        col("v.money").alias("precio_unitario"),
        col("v.money").alias("monto_total"),
        col("v.Time_of_Day").alias("franja_horaria"),
        current_timestamp().alias("fecha_procesamiento")
    )

# COMMAND ----------

df_hecho_ventas.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.HECHO_VENTAS")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Optimización

# COMMAND ----------

spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.DIM_CAFE")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.DIM_PAGO")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.DIM_FECHA")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.HECHO_VENTAS")