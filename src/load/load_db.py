from sqlalchemy import text
from src.db.connection import get_engine
from src.utils.logger import setup_logger

logger = setup_logger("load_db")

def truncate_tables(engine):
    """
    Limpia todos los datos de las tablas antes de cargar.
    Útil para pipelines de carga completa (historical).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE cryptocurrency_prices, cryptocurrency_metrics RESTART IDENTITY;"))
            conn.commit()
            conn.commit()
        logger.info("Tables truncated successfully (Historical Load).")
    except Exception as e:
        logger.error(f"Error truncating tables: {e}")

def get_latest_date(engine):
    """
    Recupera el price_timestamp más reciente de la base de datos.
    Usado para carga incremental.
    """
    try:
        query = "SELECT MAX(price_timestamp) FROM cryptocurrency_prices;"
        with engine.connect() as conn:
            result = conn.execute(text(query)).scalar()
        return pd.to_datetime(result) if result else None
    except Exception as e:
    except Exception as e:
        logger.error(f"Error fetching max date: {e}")
        return None

def filter_new_data(df, latest_date):
    """
    Filtra el DataFrame para incluir solo registros más recientes que la última fecha en la BD.
    """
    if latest_date is None:
        return df
    
    # Asegurar que la fecha del df sea datetime
    if 'date' in df.columns:
        # Normalizar para eliminar tiempo si es necesario, aunque usualmente se maneja en clean.py
        return df[df['date'] > latest_date]
    return df

def load_raw_prices_to_supabase(df, engine):
    """
    Carga datos de precios en la tabla cryptocurrency_prices.
    Renombrado de load_prices para coincidir con la solicitud del usuario.
    """
    """
    if df.empty:
        logger.warning("No price data to load.")
        return

    # Preparar DataFrame para la tabla de precios
    prices_df = df[['coin_id', 'date', 'price', 'volume', 'market_cap']].copy()
    prices_df.rename(columns={
        'coin_id': 'coin',
        'date': 'price_timestamp'
    }, inplace=True)
    
    # Añadir row_index (requerido por esquema)
    # Nota: Para incremental, esto podría necesitar continuar desde el ID máximo previo,
    # pero el esquema dice que row_index es solo "2da col de CSV", así que 0..N por carga está bien
    # O implica un índice ordenado.
    # Mantengámoslo simple: rango para el lote actual.
    prices_df['row_index'] = range(len(prices_df)) 

    table_name = 'cryptocurrency_prices'
    
    try:
        prices_df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
    try:
        prices_df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
        logger.info(f"Loaded {len(prices_df)} rows into {table_name}")
    except Exception as e:
        logger.error(f"Error loading {table_name} (likely duplicates): {e}")


def load_metrics_to_supabase(df, engine):
    """
    Carga datos de métricas en la tabla cryptocurrency_metrics.
    Renombrado de load_metrics para coincidir con la solicitud del usuario.
    """
    if df.empty:
    if df.empty:
        logger.warning("No metrics data to load.")
        return

    metrics_df = df[['coin_id', 'date', 
                     'price_change_24h', 'price_change_7d', 'price_change_30d',
                     'market_cap_change_24h', 'market_cap_change_7d', 'market_cap_change_30d',
                     'volume_change_24h', 'volume_change_7d', 'volume_change_30d']].copy()
    
    metrics_df.rename(columns={
        'coin_id': 'coin',
        'date': 'price_timestamp'
    }, inplace=True)
    
    table_name = 'cryptocurrency_metrics'
    
    try:
        metrics_df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
    try:
        metrics_df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
        logger.info(f"Loaded {len(metrics_df)} rows into {table_name}")
    except Exception as e:
        logger.error(f"Error loading {table_name} (likely duplicates): {e}")


def load_data_to_supabase(df, incremental=False):
    """
    Orquesta la carga de datos en las tablas de Supabase.
    Soporta modos Histórico (Truncate) e Incremental (Append New).
    """
    engine = get_engine()
    
    if not incremental:
        logger.info("--- Mode: HISTORICAL LOAD (Full Refresh) ---")
        truncate_tables(engine)
        df_to_load = df
    else:
        logger.info("--- Mode: INCREMENTAL LOAD ---")
        latest_date = get_latest_date(engine)
        logger.info(f"Latest date in DB: {latest_date}")
        
        df_to_load = filter_new_data(df, latest_date)
        logger.info(f"New rows to insert: {len(df_to_load)}")
    
    if df_to_load.empty:
        logger.info("Skipping load (No new data).")
        return

    logger.info("Loading Prices...")
    load_raw_prices_to_supabase(df_to_load, engine)
    
    logger.info("Loading Metrics...")
    load_metrics_to_supabase(df_to_load, engine)
