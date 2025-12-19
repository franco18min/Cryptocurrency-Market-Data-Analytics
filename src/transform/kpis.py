import pandas as pd
import numpy as np

def calculate_kpis(df):
    """
    Calcula KPIs y los añade como columnas al DataFrame.
    
    KPIs:
    1. Tendencias de Capitalización de Mercado (vía market_cap_change)
    2. Rentabilidad Mensual (profitability_30d)
    3. Volatilidad Mensual (volatility_30d)
    """
    if df.empty:
        return df

    # Asegurar que los datos estén ordenados
    df = df.sort_values(by=['coin_id', 'date'])
    
    # Calcular retornos diarios (cambio porcentual en precio)
    df['daily_return'] = df.groupby('coin_id')['price'].pct_change()
    
    # KPI 1: Cambios en Market Cap y Volumen
    df['market_cap_change_24h'] = df.groupby('coin_id')['market_cap'].pct_change(periods=1) * 100
    df['volume_change_24h'] = df.groupby('coin_id')['volume'].pct_change(periods=1) * 100
    
    # KPI 2: Rentabilidad Mensual (Aprox 30 días)
    # Calculamos el cambio porcentual comparado con hace 30 días
    df['profitability_30d'] = df.groupby('coin_id')['price'].pct_change(periods=30) * 100
    
    # KPI 3: Volatilidad
    # Desviación estándar de los retornos diarios sobre una ventana móvil de 30 días
    # Esto da una medida de la volatilidad para el mes anterior
    df['volatility_30d'] = df.groupby('coin_id')['daily_return'].rolling(window=30).std().reset_index(0, drop=True) * 100
    
    # Métricas adicionales útiles del script original
    df['price_change_24h'] = df.groupby('coin_id')['price'].pct_change(periods=1) * 100
    df['price_change_7d'] = df.groupby('coin_id')['price'].pct_change(periods=7) * 100
    df['price_change_30d'] = df.groupby('coin_id')['price'].pct_change(periods=30) * 100

    df['market_cap_change_7d'] = df.groupby('coin_id')['market_cap'].pct_change(periods=7) * 100
    df['market_cap_change_30d'] = df.groupby('coin_id')['market_cap'].pct_change(periods=30) * 100

    df['volume_change_7d'] = df.groupby('coin_id')['volume'].pct_change(periods=7) * 100
    df['volume_change_30d'] = df.groupby('coin_id')['volume'].pct_change(periods=30) * 100
    
    # Llenar NaNs generados por pct_change (las primeras filas serán NaN)
    # Podemos llenar con 0 o dejar como NaN. Dejar como NaN es más seguro para análisis,
    # pero para carga SQL, podríamos querer manejarlos.
    # Llenemos con 0 para los primeros registros donde el cambio es indefinido.
    df = df.fillna(0)
    
    return df
