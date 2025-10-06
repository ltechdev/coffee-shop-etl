# Coffee Shop ETL - Arquitectura Medallion en Databricks

Pipeline de datos automatizado para análisis de ventas de café implementando arquitectura Medallion (Bronze-Silver-Gold) en Azure Databricks con CI/CD completo.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso](#uso)
- [Modelo de Datos](#modelo-de-datos)
- [CI/CD](#cicd)
- [Conexión con Power BI](#conexión-con-power-bi)
- [Monitoreo](#monitoreo)
- [Troubleshooting](#troubleshooting)
- [Autor](#autor)

## Descripción

Pipeline ETL completo que procesa datos de ventas de una cafetería utilizando la arquitectura Medallion en Azure Databricks. El proyecto implementa buenas prácticas de ingeniería de datos con separación de capas, automatización mediante CI/CD, y entrega de datos listos para análisis de negocio.

## Arquitectura

### Flujo de Datos
CSV (Raw Data)
↓
Bronze Layer (Ingesta sin transformación)
↓
Silver Layer (Limpieza + Modelo Dimensional)
↓
Gold Layer (Agregaciones de Negocio)
↓
Power BI (Visualización)

### Capas del Pipeline

#### Bronze Layer
- **Propósito**: Almacenar datos crudos tal como vienen de la fuente
- **Tabla**: `VENTA_CAFE`
- **Contenido**: Datos sin transformar con timestamp de ingesta

#### Silver Layer
- **Propósito**: Datos limpios y normalizados en modelo dimensional (Star Schema)
- **Tablas**:
  - `HECHO_VENTAS`: Tabla de hechos con transacciones de venta
  - `DIM_CAFE`: Dimensión de productos con categorización
  - `DIM_PAGO`: Dimensión de métodos de pago
  - `DIM_FECHA`: Dimensión calendario para análisis temporal

#### Gold Layer
- **Propósito**: Agregados optimizados para consumo de negocio
- **Tablas**:
  - `AGG_VENTAS_DIARIAS`: Métricas diarias
  - `AGG_VENTAS_POR_CAFE`: Performance por producto
  - `AGG_VENTAS_POR_PAGO`: Distribución de métodos de pago
  - `AGG_VENTAS_POR_DIA_SEMANA`: Patrones semanales
  - `AGG_VENTAS_POR_FRANJA_HORARIA`: Análisis por hora del día
  - `AGG_TOP_PRODUCTOS`: Ranking mensual de productos
  - `AGG_RESUMEN_MENSUAL`: Dashboard ejecutivo mensual

## Estructura del Proyecto

coffee-shop-etl/
├── .github/
│   └── workflows/
│       └── databricks-deploy.yml
├── proceso/
│   ├── 1-Ddls-Medallion.sql
│   ├── 2-Ingest-Coffee-Shop-Data.py
│   ├── 3-Transform.py
│   └── 4-Load.py
└── README.md


## Tecnologías

- **Azure Databricks**: Motor de procesamiento distribuido
- **Delta Lake**: Formato ACID transaccional
- **PySpark**: Transformaciones de datos
- **Azure Data Lake Storage Gen2**: Almacenamiento persistente
- **GitHub Actions**: CI/CD automatizado
- **Power BI**: Visualización y análisis

## Requisitos Previos

- Cuenta de Azure con acceso a Databricks
- Workspace de Databricks configurado
- Cluster activo (nombre: `CLUSTER COFFEE SHOP`)
- Cuenta de GitHub
- Azure Data Lake Storage Gen2 configurado
- Power BI Desktop (opcional para visualización)

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/coffee-shop-etl.git
cd coffee-shop-etl

2. Configurar Databricks Personal Access Token

En Databricks: User Settings → Developer → Access Tokens
Click en Generate New Token
Comment: "GitHub CI/CD"
Lifetime: 90 days
Copiar y guardar el token de forma segura

3. Configurar GitHub Secrets
En tu repositorio de GitHub:

Settings → Secrets and variables → Actions
Click en New repository secret
Agregar los siguientes secrets:

Nombre: DATABRICKS_HOST
Valor: https://adb-xxxxxxxxxxxxx.azuredatabricks.net

Nombre: DATABRICKS_TOKEN
Valor: dapi_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

4. Verificar Configuración de Storage
Asegurarse de que el storage path esté correctamente configurado:

abfss://coffeeshop@adlsdevluis25.dfs.core.windows.net

Uso
Despliegue Automático
El pipeline se despliega y ejecuta automáticamente al hacer push a master:

git add .
git commit -m "Update pipeline"
git push origin master

GitHub Actions ejecutará:

Despliegue de notebooks a /prod/coffee_shop
Creación del workflow CoffeeShopWFDeploy
Ejecución completa del pipeline: DDL → Bronze → Silver → Gold
Monitoreo de la ejecución

Despliegue Manual
Para ejecutar manualmente desde GitHub:

Ir al tab Actions en GitHub
Seleccionar Coffee Shop ETL - Databricks Deploy
Click en Run workflow
Seleccionar rama master
Click en Run workflow

Ejecución Local en Databricks
Si prefieres ejecutar notebooks manualmente:

Navegar a /prod/coffee_shop en Databricks
Ejecutar notebooks en orden:

1-Ddls-Medallion
2-Ingest-Coffee-Shop-Data
3-Transform
4-Load



Modelo de Datos
Silver Layer - Modelo Dimensional
Tabla de Hechos: HECHO_VENTAS

HECHO_VENTAS
├── fecha: DATE (FK → DIM_FECHA)
├── hora: TIMESTAMP
├── id_cafe: INT (FK → DIM_CAFE)
├── id_pago: INT (FK → DIM_PAGO)
├── cantidad: INT
├── precio_unitario: DOUBLE
├── monto_total: DOUBLE
├── franja_horaria: STRING
└── fecha_procesamiento: TIMESTAMP



Dimensiones
DIM_CAFE

id_cafe (PK): Identificador único del producto
coffee_name: Nombre del café
categoria: Espresso, Latte, Bebida Fría, Otros
tamanio: Grande, Mediano, Pequeño
precio_base: Precio promedio histórico
activo: Estado del producto
fecha_vigencia: Fecha de alta

DIM_PAGO

id_pago (PK): Identificador del método de pago
cash_type: card, cash, online
proveedor: Visa/Mastercard, PayPal, null
activo: Estado del método

DIM_FECHA

fecha (PK): Fecha completa
anio, trimestre, mes
Month_name, Monthsort
dia_semana, Weekday, Weekdaysort
dia_del_mes
es_fin_semana, es_feriado

Gold Layer - Agregados de Negocio
Todas las tablas Gold incluyen:

Métricas agregadas específicas por dimensión
ultima_actualizacion: Timestamp de última actualización
Campos calculados relevantes para análisis

CI/CD
Pipeline de GitHub Actions
El workflow automatiza el ciclo completo:

Deploy: Despliega notebooks desde GitHub a Databricks
Workflow Management: Elimina workflow antiguo si existe
Cluster Lookup: Encuentra el cluster configurado
Workflow Creation: Crea workflow con 4 tareas secuenciales
Execution: Ejecuta pipeline automáticamente
Monitoring: Monitorea ejecución cada 30 segundos
Notifications: Envía email en caso de error

Configuración del Workflow Databricks

Tasks:
├── create_tables_ddl (30min, 1 retry)
├── ingest_bronze (60min, 2 retries)
├── transform_silver (60min, 2 retries)
└── aggregate_gold (60min, 2 retries)

Schedule: Diario 10:00 AM (Lima)
Timeout total: 4 horas
Max concurrent runs: 1
Email notifications: lchaponant@gmail.com

Conexión con Power BI
Prerequisitos

SQL Warehouse activo en Databricks
Personal Access Token generado
Power BI Desktop instalado

Pasos de Conexión
1. Obtener Credenciales de Databricks
En Databricks:

SQL Warehouses → Seleccionar tu warehouse
Tab Connection Details
Copiar:

Server hostname: adb-xxxxx.azuredatabricks.net
HTTP Path: /sql/1.0/warehouses/xxxxx



2. Conectar Power BI Desktop
1. Abrir Power BI Desktop
2. Get Data → More → Azure Databricks
3. Ingresar credenciales:
   - Server hostname: [valor copiado]
   - HTTP Path: [valor copiado]
   - Data Connectivity mode: DirectQuery (recomendado)
4. Autenticación:
   - Método: Personal Access Token
   - Token: [tu token de Databricks]
5. Click Connect

3. Seleccionar Tablas Gold
En el Navigator, expandir:

catalog_prod
└── golden
    ├── AGG_VENTAS_DIARIAS
    ├── AGG_VENTAS_POR_CAFE
    ├── AGG_VENTAS_POR_PAGO
    ├── AGG_VENTAS_POR_DIA_SEMANA
    ├── AGG_VENTAS_POR_FRANJA_HORARIA
    ├── AGG_TOP_PRODUCTOS
    └── AGG_RESUMEN_MENSUAL

Seleccionar las tablas necesarias y click en Load.
4. Configurar Modo de Conectividad
DirectQuery (Recomendado)

Datos siempre actualizados
No ocupa espacio en Power BI
Queries se ejecutan en Databricks

Import Mode

Más rápido para visualizaciones
Requiere refresh programado
Limitación de volumen de datos

Dashboards Recomendados

Ventas Diarias: Line chart con tendencias temporales
Top Productos: Bar chart con ranking de cafés
Análisis de Pagos: Pie chart con distribución
Patrones Horarios: Heatmap de ventas por hora
Resumen Ejecutivo: KPIs consolidados con cards

Monitoreo
En Databricks

Workflows:

Ir a Workflows en el menú lateral
Buscar CoffeeShopWFDeploy
Ver historial de ejecuciones


Logs por Tarea:

Click en una ejecución específica
Click en cada tarea para ver logs detallados
Revisar stdout/stderr en caso de errores



En GitHub Actions

Tab Actions del repositorio
Ver historial de workflows
Click en ejecución específica para detalles
Revisar logs de cada step

Notificaciones

Email: Configurado para enviar a lchaponant@gmail.com en caso de fallo
GitHub: Notificaciones en el repositorio


Autor
Luis Alberto Chaponan Tejada
Email: lchaponant@gmail.com
LinkedIn: https://www.linkedin.com/in/luis-chaponan-tejada/
GitHub: ltechdev

Proyecto: Data Engineering - Arquitectura Medallion
Tecnología: Azure Databricks + Delta Lake + CI/CD
Última actualización: 2025
Licencia
MIT License - Ver archivo LICENSE para más detalles