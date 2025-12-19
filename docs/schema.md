# Esquema de Datos y KPIs

## Esquema de Base de Datos
Los datos se almacenan en una base de datos PostgreSQL en la tabla `crypto_market_data` (o tablas divididas `cryptocurrency_prices` y `cryptocurrency_metrics`).

| Columna | Tipo | Descripción |
|--------|------|-------------|
| `coin_id` | String | Identificador de la criptomoneda (ej., 'bitcoin') |
| `date` | DateTime | Fecha del registro |
| `price` | Float | Precio de cierre en USD |
| `volume` | Float | Volumen de trading 24h |
| `market_cap` | Float | Capitalización de mercado en USD |
| `daily_return` | Float | Cambio porcentual diario en el precio |
| `market_cap_change_24h` | Float | Cambio porcentual 24h en Market Cap |
| `volume_change_24h` | Float | Cambio porcentual 24h en Volumen |
| `profitability_30d` | Float | Cambio porcentual en precio sobre los últimos 30 días (Retorno Mensual) |
| `volatility_30d` | Float | Desviación estándar de retornos diarios sobre los últimos 30 días (Volatilidad Mensual) |
| `price_change_24h` | Float | Cambio porcentual 24h en precio |
| `price_change_7d` | Float | Cambio porcentual 7d en precio |

## Definición de KPIs

### 1. Tendencias de Capitalización de Mercado
- **Métrica**: `market_cap` y `market_cap_change_24h`
- **Objetivo**: Entender el comportamiento de las criptomonedas basado en su tamaño de mercado.
- **Fuente**: Datos crudos de CoinGecko `market_caps`.

### 2. Rentabilidad Mensual
- **Métrica**: `profitability_30d`
- **Cálculo**: `(Precio_t / Precio_t-30) - 1`
- **Meta**: Aumento del 5% mensual (Objetivo).

### 3. Volatilidad Mensual
- **Métrica**: `volatility_30d`
- **Cálculo**: Desviación estándar móvil de `daily_return` sobre una ventana de 30 días.
- **Meta**: Disminución de 1% mensual (Objetivo).

## Estructura del Pipeline
- **Extracción**: `src/etl/extract.py` - Obtiene datos crudos de CoinGecko.
- **Transformación**: 
    - `src/transform/clean.py` - Limpia y formatea los datos.
    - `src/transform/kpis.py` - Calcula los KPIs definidos arriba.
- **Carga**: `src/load/load_db.py` - Carga los datos procesados en PostgreSQL.
