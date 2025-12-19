-- Consultas Analíticas Avanzadas
-- Diseñadas para PostgreSQL (Supabase / Render / Railway)

-- 1. Rankings de Volatilidad Mensual
-- Clasifica las monedas por su volatilidad en los últimos 30 días.
WITH monthly_stats AS (
    SELECT 
        coin as coin_id, -- Ajuste a nombre de columna real si es necesario
        STDDEV(price) / AVG(price) * 100 as volatility_coef_var, -- Coeficiente de variación como proxy simple si daily_return no está en columna
        -- Nota: Si tienes daily_return precalculado en KPIs, úsalo.
        -- Asumiendo tabla de métricas separada o join, aquí hacemos un ejemplo simple sobre precios.
        AVG(price) as avg_price
    FROM cryptocurrency_prices
    WHERE price_timestamp > NOW() - INTERVAL '30 days'
    GROUP BY coin
)
SELECT 
    coin_id,
    volatility_coef_var,
    RANK() OVER (ORDER BY volatility_coef_var DESC) as risk_rank
FROM monthly_stats
ORDER BY risk_rank ASC;

-- 2. Detección de Días de Alto Crecimiento ("Pump Days")
-- Días donde el precio subió significativamente (ej. > 10% vs el día anterior)
SELECT 
    p1.coin,
    p1.price_timestamp,
    p1.price,
    (p1.price - p2.price) / p2.price * 100 as daily_growth_pct
FROM cryptocurrency_prices p1
JOIN cryptocurrency_prices p2 
  ON p1.coin = p2.coin 
  AND p2.price_timestamp = p1.price_timestamp - INTERVAL '1 day'
WHERE (p1.price - p2.price) / p2.price > 0.10 -- Filtro de crecimiento > 10%
ORDER BY daily_growth_pct DESC;

-- 3. Volumen Acumulado Mensual
SELECT 
    coin,
    DATE_TRUNC('month', price_timestamp) as mes,
    SUM(volume) as volumen_total_mes
FROM cryptocurrency_prices
GROUP BY coin, mes
ORDER BY mes DESC, volumen_total_mes DESC;
