-- Schema para Supabase (PostgreSQL)
-- Copiar y pegar esto en el SQL Editor de Supabase

-- Tabla: cryptocurrency_prices
-- Almacena los datos crudos/normalizados de precios detectados por el ETL.
CREATE TABLE IF NOT EXISTS cryptocurrency_prices (
    row_index BIGINT,
    coin TEXT NOT NULL,
    price_timestamp TIMESTAMP NOT NULL,
    price NUMERIC,
    volume NUMERIC,
    market_cap NUMERIC,
    PRIMARY KEY (coin, price_timestamp)
);

-- Tabla: cryptocurrency_metrics
-- Almacena los KPIs calculados.
CREATE TABLE IF NOT EXISTS cryptocurrency_metrics (
    coin TEXT NOT NULL,
    price_timestamp TIMESTAMP NOT NULL,
    price_change_24h NUMERIC,
    price_change_7d NUMERIC,
    price_change_30d NUMERIC,
    market_cap_change_24h NUMERIC,
    market_cap_change_7d NUMERIC,
    market_cap_change_30d NUMERIC,
    volume_change_24h NUMERIC,
    volume_change_7d NUMERIC,
    volume_change_30d NUMERIC,
    PRIMARY KEY (coin, price_timestamp)
);

-- Índices para mejorar rendimiento de consultas por fecha
CREATE INDEX IF NOT EXISTS idx_prices_date ON cryptocurrency_prices(price_timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON cryptocurrency_metrics(price_timestamp);
