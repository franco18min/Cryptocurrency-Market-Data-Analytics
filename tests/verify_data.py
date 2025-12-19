import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.connection import get_engine

def verify_data():
    engine = get_engine()
    
    print("--- Verificando Datos en Supabase ---\n")
    
    # 1. Contar registros
    print("1. Conteo de registros:")
    count_prices = pd.read_sql("SELECT COUNT(*) FROM cryptocurrency_prices;", engine)
    count_metrics = pd.read_sql("SELECT COUNT(*) FROM cryptocurrency_metrics;", engine)
    print(f"   - cryptocurrency_prices: {count_prices.iloc[0, 0]} filas")
    print(f"   - cryptocurrency_metrics: {count_metrics.iloc[0, 0]} filas")
    print("-" * 30)

    # 2. Muestra de Precios (Bitcoin últimos 5 días)
    print("\n2. Últimos 5 registros de Precios (Bitcoin):")
    query_prices = """
    SELECT coin, price_timestamp, price, volume, market_cap 
    FROM cryptocurrency_prices 
    WHERE coin = 'bitcoin' 
    ORDER BY price_timestamp DESC 
    LIMIT 5;
    """
    df_prices = pd.read_sql(query_prices, engine)
    print(df_prices.to_string(index=False))
    print("-" * 30)

    # 3. Muestra de Métricas (Bitcoin últimos 5 días)
    print("\n3. Últimos 5 registros de Métricas (Bitcoin):")
    query_metrics = """
    SELECT coin, price_timestamp, price_change_24h, volatility_30d 
    FROM cryptocurrency_metrics 
    WHERE coin = 'bitcoin' 
    ORDER BY price_timestamp DESC 
    LIMIT 5;
    """
    # Note: verify if volatility_30d exists in the new schema. 
    # User schema input: price_change_24h, price_change_7d, price_change_30d, market_cap_... volume_...
    # The user input schema for metrics did NOT explicitly list 'volatility_30d' or 'profitability_30d'.
    # However, my kpis.py calculates them. 
    # Let's check if I added them to the load function?
    # I should check src/load/load_db.py again to see what columns were loaded.
    
    # Wait, looking at previous turn load_db.py:
    # metrics_df = df[['coin_id', 'date', 'price_change_24h', ... 'volume_change_30d']].copy()
    # I did NOT include volatility_30d in the load_metrics function in the previous turn!
    # The user schema provided in the prompt was strictly changes (24h, 7d, 30d).
    # So I should query columns that exist.
    
    query_metrics_safe = """
    SELECT coin, price_timestamp, price_change_24h, price_change_7d, price_change_30d
    FROM cryptocurrency_metrics 
    WHERE coin = 'bitcoin' 
    ORDER BY price_timestamp DESC 
    LIMIT 5;
    """
    df_metrics = pd.read_sql(query_metrics_safe, engine)
    print(df_metrics.to_string(index=False))
    print("-" * 30)
    
    # 4. Join Check
    print("\n4. Verificación de Integridad (Join):")
    query_join = """
    SELECT p.coin, p.price_timestamp, p.price, m.price_change_24h
    FROM cryptocurrency_prices p
    JOIN cryptocurrency_metrics m ON p.coin = m.coin AND p.price_timestamp = m.price_timestamp
    WHERE p.coin = 'ethereum'
    ORDER BY p.price_timestamp DESC
    LIMIT 5;
    """
    df_join = pd.read_sql(query_join, engine)
    print(df_join.to_string(index=False))

if __name__ == "__main__":
    verify_data()
