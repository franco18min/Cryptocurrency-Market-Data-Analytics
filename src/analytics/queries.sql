-- Advanced Analytical Queries for Crypto Market Data
-- Intended for PostgreSQL (Supabase / Render / Railway)

-- 1. Moving Averages & Trend Analysis (Window Function)
-- Calculates the 7-day and 30-day moving average of prices for each coin
-- Helps identify if the current price is above/below the short/long term trend.
SELECT 
    coin_id,
    date,
    price,
    AVG(price) OVER (
        PARTITION BY coin_id 
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as ma_7d,
    AVG(price) OVER (
        PARTITION BY coin_id 
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as ma_30d
FROM crypto_market_data
WHERE date > NOW() - INTERVAL '3 months'
ORDER BY coin_id, date DESC;

-- 2. Monthly Volatility Ranking (Aggregates & Ranking)
-- Ranks coins by their volatility in the last 30 days.
-- Useful to identify the riskiest assets recently.
WITH monthly_stats AS (
    SELECT 
        coin_id,
        STDDEV(daily_return) * 100 as volatility_stddev,
        AVG(daily_return) * 100 as avg_daily_return
    FROM crypto_market_data
    WHERE date > NOW() - INTERVAL '30 days'
    GROUP BY coin_id
)
SELECT 
    coin_id,
    volatility_stddev,
    avg_daily_return,
    RANK() OVER (ORDER BY volatility_stddev DESC) as risk_rank
FROM monthly_stats
ORDER BY risk_rank ASC;

-- 3. Cumulative Volume & Market Share (Window Function & Partition)
-- Calculates cumulative volume for the current month and the % contribution 
-- of each day's volume to the monthly total so far.
SELECT 
    coin_id,
    date,
    volume,
    SUM(volume) OVER (
        PARTITION BY coin_id, DATE_TRUNC('month', date)
        ORDER BY date
    ) as cumulative_monthly_volume,
    volume / SUM(volume) OVER (
        PARTITION BY coin_id, DATE_TRUNC('month', date)
    ) * 100 as pct_of_total_month_volume
FROM crypto_market_data
WHERE date > NOW() - INTERVAL '2 months'
ORDER BY coin_id, date DESC;

-- 4. High Growth Days (Filtering Aggregated Windows)
-- Identifies "Pump" days where the daily return was more than 2 standard deviations
-- above the average daily return for that coin in the same year.
WITH coin_yearly_stats AS (
    SELECT 
        coin_id,
        EXTRACT(YEAR FROM date) as year,
        AVG(daily_return) as avg_return,
        STDDEV(daily_return) as std_return
    FROM crypto_market_data
    GROUP BY coin_id, EXTRACT(YEAR FROM date)
)
SELECT 
    m.coin_id,
    m.date,
    m.daily_return * 100 as daily_return_pct,
    s.avg_return * 100 as avg_return_pct,
    (m.daily_return - s.avg_return) / NULLIF(s.std_return, 0) as z_score
FROM crypto_market_data m
JOIN coin_yearly_stats s 
    ON m.coin_id = s.coin_id 
    AND EXTRACT(YEAR FROM m.date) = s.year
WHERE (m.daily_return - s.avg_return) > (2 * s.std_return)
ORDER BY m.date DESC;
