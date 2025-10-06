# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transformación Silver → Gold
# MAGIC Pipeline de agregaciones de negocio para análisis

# COMMAND ----------

# MAGIC %md
# MAGIC ### Configuración

# COMMAND ----------

catalogo = "catalog_dev"
esquema_origen = "silver"
esquema_destino = "golden"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Lectura de Tablas Silver

# COMMAND ----------

df_hecho_ventas = spark.table(f"{catalogo}.{esquema_origen}.HECHO_VENTAS")
df_dim_cafe = spark.table(f"{catalogo}.{esquema_origen}.DIM_CAFE")
df_dim_pago = spark.table(f"{catalogo}.{esquema_origen}.DIM_PAGO")
df_dim_fecha = spark.table(f"{catalogo}.{esquema_origen}.DIM_FECHA")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_VENTAS_DIARIAS

# COMMAND ----------

df_ventas_diarias = df_hecho_ventas\
    .groupBy("fecha")\
    .agg(
        sum("monto_total").alias("ingresos_totales"),
        count("*").alias("total_transacciones"),
        avg("monto_total").alias("ticket_promedio"),
        sum("cantidad").alias("cantidad_total_vendida"),
        countDistinct("id_cafe").alias("productos_unicos_vendidos")
    )\
    .withColumn("ultima_actualizacion", current_timestamp())\
    .orderBy("fecha")

# COMMAND ----------

df_ventas_diarias.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_VENTAS_DIARIAS")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_VENTAS_POR_CAFE

# COMMAND ----------

df_ventas_cafe_agg = df_hecho_ventas.alias("h")\
    .join(df_dim_cafe.alias("c"), col("h.id_cafe") == col("c.id_cafe"), "inner")\
    .groupBy("h.id_cafe", "c.coffee_name", "c.categoria")\
    .agg(
        sum("h.monto_total").alias("ingresos_totales"),
        count("*").alias("total_transacciones"),
        sum("h.cantidad").alias("cantidad_total_vendida"),
        avg("h.monto_total").alias("ticket_promedio")
    )

# COMMAND ----------

df_ventas_cafe_ranked = df_ventas_cafe_agg\
    .orderBy(desc("ingresos_totales"))\
    .limit(1000)\
    .select("*", monotonically_increasing_id().alias("ranking_ingresos"))\
    .withColumn("ranking_ingresos", col("ranking_ingresos") + 1)\
    .withColumn("ultima_actualizacion", current_timestamp())

# COMMAND ----------

df_ventas_cafe_ranked.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_VENTAS_POR_CAFE")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_VENTAS_POR_PAGO

# COMMAND ----------

df_total_ventas = df_hecho_ventas.agg(sum("monto_total")).collect()[0][0]

# COMMAND ----------

df_ventas_pago = df_hecho_ventas.alias("h")\
    .join(df_dim_pago.alias("p"), col("h.id_pago") == col("p.id_pago"), "inner")\
    .groupBy("p.cash_type", "p.proveedor")\
    .agg(
        sum("h.monto_total").alias("ingresos_totales"),
        count("*").alias("total_transacciones"),
        avg("h.monto_total").alias("ticket_promedio")
    )\
    .withColumn("participacion_pct", round((col("ingresos_totales") / lit(df_total_ventas)) * 100, 2))\
    .withColumn("ultima_actualizacion", current_timestamp())\
    .orderBy(desc("ingresos_totales"))

# COMMAND ----------

df_ventas_pago.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_VENTAS_POR_PAGO")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_VENTAS_POR_DIA_SEMANA

# COMMAND ----------

df_ventas_dia_semana = df_hecho_ventas.alias("h")\
    .join(df_dim_fecha.alias("f"), col("h.fecha") == col("f.fecha"), "inner")\
    .groupBy("f.Weekday", "f.Weekdaysort")\
    .agg(
        sum("h.monto_total").alias("ingresos_totales"),
        count("*").alias("total_transacciones"),
        avg("h.monto_total").alias("ticket_promedio"),
        countDistinct("h.fecha").alias("dias_con_ventas")
    )\
    .withColumn("ingreso_promedio_diario", round(col("ingresos_totales") / col("dias_con_ventas"), 2))\
    .withColumn("ultima_actualizacion", current_timestamp())\
    .drop("dias_con_ventas")\
    .orderBy("Weekdaysort")

# COMMAND ----------

df_ventas_dia_semana.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_VENTAS_POR_DIA_SEMANA")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_VENTAS_POR_FRANJA_HORARIA

# COMMAND ----------

df_ventas_franja = df_hecho_ventas\
    .groupBy("franja_horaria")\
    .agg(
        sum("monto_total").alias("ingresos_totales"),
        count("*").alias("total_transacciones"),
        avg("monto_total").alias("ticket_promedio"),
        max(hour("hora")).alias("hora_pico")
    )\
    .withColumn("ultima_actualizacion", current_timestamp())\
    .orderBy(
        when(col("franja_horaria") == "morning", lit(1))
        .when(col("franja_horaria") == "afternoon", lit(2))
        .when(col("franja_horaria") == "evening", lit(3))
        .otherwise(lit(4))
    )

# COMMAND ----------

df_ventas_franja.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_VENTAS_POR_FRANJA_HORARIA")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_TOP_PRODUCTOS

# COMMAND ----------

df_productos_periodo = (
    df_hecho_ventas.alias("h")
    .join(df_dim_cafe.alias("c"), F.col("h.id_cafe") == F.col("c.id_cafe"), "inner")
    .join(df_dim_fecha.alias("f"), F.col("h.fecha") == F.col("f.fecha"), "inner")
    .groupBy(
        F.col("f.anio"),
        F.col("f.mes"),
        F.col("h.id_cafe"),
        F.col("c.coffee_name"),
        F.col("c.categoria")
    )
    .agg(
        F.sum("h.monto_total").alias("ingresos_totales"),
        F.sum("h.cantidad").alias("cantidad_total")
    )
)


# COMMAND ----------

df_top_productos = (
    df_productos_periodo
    .groupBy("anio", "mes")
    .agg(
        F.collect_list(
            F.struct(
                F.col("ingresos_totales"),
                F.col("id_cafe"),
                F.col("coffee_name"),
                F.col("categoria"),
                F.col("cantidad_total")
            )
        ).alias("productos")
    )
    .withColumn("productos", F.expr("slice(array_sort(productos, (left, right) -> case when left.ingresos_totales > right.ingresos_totales then -1 when left.ingresos_totales < right.ingresos_totales then 1 else 0 end), 1, 10)"))
    .withColumn("periodo_analisis", F.lit("mensual"))
    .withColumn("fecha_inicio", F.expr("make_date(anio, mes, 1)"))
    .withColumn("fecha_fin", F.expr("last_day(make_date(anio, mes, 1))"))
    .withColumn("ultima_actualizacion", F.current_timestamp())
)


# COMMAND ----------

df_top_productos = (
    df_top_productos
    .withColumn("producto", F.explode("productos"))
    .select(
        "periodo_analisis",
        "fecha_inicio",
        "fecha_fin",
        F.col("producto.id_cafe"),
        F.col("producto.coffee_name"),
        F.col("producto.categoria"),
        F.col("producto.ingresos_totales"),
        F.col("producto.cantidad_total"),
        "ultima_actualizacion"
    )
)

# COMMAND ----------

df_top_productos.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_TOP_PRODUCTOS")

# COMMAND ----------

# MAGIC %md
# MAGIC ### AGG_RESUMEN_MENSUAL

# COMMAND ----------

df_resumen_base = (
    df_hecho_ventas.alias("h")
    .join(df_dim_fecha.alias("f"), F.col("h.fecha") == F.col("f.fecha"), "inner")
    .groupBy("f.anio", "f.mes", "f.Month_name")
    .agg(
        F.sum("h.monto_total").alias("ingresos_totales"),
        F.count("*").alias("total_transacciones"),
        F.round(F.avg("h.monto_total"), 2).alias("ticket_promedio")
    )
)

# COMMAND ----------

df_cafe_top = (
    df_hecho_ventas.alias("h")
    .join(df_dim_fecha.alias("f"), F.col("h.fecha") == F.col("f.fecha"), "inner")
    .join(df_dim_cafe.alias("c"), F.col("h.id_cafe") == F.col("c.id_cafe"), "inner")
    .groupBy("f.anio", "f.mes", "c.coffee_name")
    .agg(F.sum("h.cantidad").alias("cantidad"))
)

df_cafe_mes = (
    df_cafe_top
    .groupBy("anio", "mes")
    .agg(F.first(F.col("coffee_name")).alias("cafe_mas_vendido"))
)

# COMMAND ----------

df_pago_top = (
    df_hecho_ventas.alias("h")
    .join(df_dim_fecha.alias("f"), F.col("h.fecha") == F.col("f.fecha"), "inner")
    .join(df_dim_pago.alias("p"), F.col("h.id_pago") == F.col("p.id_pago"), "inner")
    .groupBy("f.anio", "f.mes", "p.cash_type")
    .agg(F.count("*").alias("transacciones"))
)

df_pago_mes = (
    df_pago_top
    .groupBy("anio", "mes")
    .agg(F.first(F.col("cash_type")).alias("metodo_pago_principal"))
)
# COMMAND ----------

df_dia_top = (
    df_hecho_ventas.alias("h")
    .join(df_dim_fecha.alias("f"), F.col("h.fecha") == F.col("f.fecha"), "inner")
    .groupBy("f.anio", "f.mes", "f.Weekday")
    .agg(F.sum("h.monto_total").alias("ingresos"))
)
df_dia_mes = (
    df_dia_top
    .groupBy("anio", "mes")
    .agg(F.first(F.col("Weekday")).alias("dia_semana_mas_fuerte"))
)

# COMMAND ----------

df_resumen_mensual = (
    df_resumen_base
    .join(df_cafe_mes, ["anio", "mes"], "left")
    .join(df_pago_mes, ["anio", "mes"], "left")
    .join(df_dia_mes, ["anio", "mes"], "left")
    .withColumn("ultima_actualizacion", F.current_timestamp())
    .orderBy("anio", "mes")
)

# COMMAND ----------

df_resumen_mensual.write.mode("overwrite").saveAsTable(f"{catalogo}.{esquema_destino}.AGG_RESUMEN_MENSUAL")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Optimización

# COMMAND ----------

spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_VENTAS_DIARIAS")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_VENTAS_POR_CAFE")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_VENTAS_POR_PAGO")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_VENTAS_POR_DIA_SEMANA")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_VENTAS_POR_FRANJA_HORARIA")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_TOP_PRODUCTOS")
spark.sql(f"OPTIMIZE {catalogo}.{esquema_destino}.AGG_RESUMEN_MENSUAL")