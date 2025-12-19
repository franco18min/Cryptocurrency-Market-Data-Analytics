import pandas as pd

def clean_data(df):
    """
    Realiza una limpieza básica en los datos crudos de criptomonedas.
    """
    if df.empty:
        return df
    
    # Convertir timestamp a datetime y normalizar para eliminar el componente de tiempo (00:00:00)
    # Esto asegura que no tengamos duplicados para el mismo día (ej. 00:00 vs hora actual)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
    
    # Eliminar la columna timestamp original si no se necesita.
    # Mantenemos 'date' para mejor legibilidad e indexación.
    
    # Verificar duplicados
    df = df.drop_duplicates(subset=['coin_id', 'date'])
    
    # Manejar valores faltantes si los hay (aunque improbable desde este endpoint para monedas mayores)
    df = df.dropna(subset=['price', 'volume', 'market_cap'])
    
    # Ordenar por moneda y fecha
    df = df.sort_values(by=['coin_id', 'date'])
    
    return df
