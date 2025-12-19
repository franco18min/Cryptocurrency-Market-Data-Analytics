# Diseño del Modelo de Datos y Estrategia de Carga (ETL)

## 1. Diseño del Modelo de Datos

El diseño óptimo para este proyecto en Supabase (PostgreSQL) sigue un esquema **estrella simplificado** o **tabular desnormalizado** dependiendo de las necesidades de BI. Para este caso, hemos optado por separar los datos "crudos" de precios de las métricas calculadas para mantener claridad y escalabilidad.

### Tablas Principales

#### `cryptocurrency_prices` (Hechos)
Almacena la serie temporal fundamental. Es la fuente de la verdad para precios y volúmenes.
- **PK**: `(coin, price_timestamp)` - Garantiza unicidad por moneda y tiempo.
- **Columnas**: `price`, `volume`, `market_cap`.
- **Uso**: Gráficos de línea base, análisis histórico de velas.

#### `cryptocurrency_metrics` (Métricas Agregadas)
Almacena los KPIs pre-calculados por el pipeline de Python. Esto descarga complejidad de PowerBI/Tableau, ya que no necesitan calcular volatilidades o ventanas móviles al vuelo.
- **PK**: `(coin, price_timestamp)`
- **Columnas**: `price_change_24h`, `volatility_30d`, `profitability_30d`.
- **Uso**: Tablas de resumen, indicadores de riesgo, alertas.

---

## 2. Estrategia de Carga (ETL Strategy)

El pipeline soporta dos modalidades fundamentales para garantizar tanto la integridad histórica como la frescura diaria.

### A. Carga Histórica (Full Refresh / Backfill)
Se ejecuta la primera vez o cuando se necesita reconstruir la base de datos completa (ej. cambio en lógica de KPIs).

1. **Truncamiento**: Se ejecuta `TRUNCATE TABLE` para limpiar tablas existentes.
2. **Extracción Masiva**: Se solicitan 365+ días de historia a la API.
3. **Batch Insert**: Se insertan los registros en lotes (`chunksize=1000`) para eficiencia.

**Comando:**
```bash
python -m src.main
# (Sin argumentos, el default es full load/truncate)
```

### B. Carga Incremental (Daily Update)
Se ejecuta diariamente (ej. vía Cron o Airflow) para mantener los datos al día sin reprocesar todo el historial.

1. **Identificación de Estado**: Consultamos `MAX(price_timestamp)` en Supabase para saber cuál fue el último dato cargado.
2. **Extracción Diferencial**: Consultamos la API (o filtramos en memoria) para obtener solo registros posteriores a esa fecha.
    - *Nota*: CoinGecko API gratuita a veces obliga a traer más días, por lo que el filtrado en Python (`filter_new_data`) es crucial.
3. **Append**: Se insertan solo las filas nuevas usando `if_exists='append'`.

**Comando:**
```bash
python -m src.main --incremental
```

## 3. Flujo De Datos
1. **API (CoinGecko)** -> JSON raw.
2. **Pandas (Transform)** -> Limpieza, conversión de fechas, cálculo de Rolling Windows (KPIs).
3. **SQLAlchemy (Load)** -> Inserta en Postgres.
4. **Data Quality** -> Verifica nulos y duplicados post-carga.
