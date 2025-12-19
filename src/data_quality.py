from sqlalchemy import text
from src.utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger("data_quality")

def check_no_nulls(engine):
    """
    Verifica que no existan valores NULL en columnas críticas: coin, price_timestamp, price.
    """
    logger.info("Ejecutando check: No hay NULLs en columnas críticas...")
    
    query = """
    SELECT COUNT(*) 
    FROM cryptocurrency_prices 
    WHERE coin IS NULL 
       OR price_timestamp IS NULL 
       OR price IS NULL;
    """
    
    with engine.connect() as conn:
        count = conn.execute(text(query)).scalar()
        
    if count > 0:
        msg = f"FALLÓ Data Quality Check: Se encontraron {count} filas con NULLs en coin/date/price."
        logger.error(msg)
        raise ValueError(msg)
    
    logger.info("PASÓ: No se encontraron valores NULL.")

def check_duplicates(engine):
    """
    Verifica que no haya duplicados para la combinación (coin, price_timestamp).
    """
    logger.info("Ejecutando check: No hay fechas duplicadas por symbol...")
    
    query = """
    SELECT coin, price_timestamp, COUNT(*)
    FROM cryptocurrency_prices
    GROUP BY coin, price_timestamp
    HAVING COUNT(*) > 1
    LIMIT 5;
    """
    
    with engine.connect() as conn:
        results = conn.execute(text(query)).fetchall()
        
    if results:
        msg = f"FALLÓ Data Quality Check: Se encontraron duplicados (ejemplo: {results})"
        logger.error(msg)
        raise ValueError("Se encontraron registros duplicados para el mismo coin y fecha.")
        
    logger.info("PASÓ: No se encontraron duplicados.")

def check_data_freshness(engine, max_days_lag=2):
    """
    Confirma que la fecha máxima en la base de datos sea reciente (cercana a hoy).
    """
    logger.info("Ejecutando check: Frescura de datos...")
    
    query = "SELECT MAX(price_timestamp) FROM cryptocurrency_prices;"
    
    with engine.connect() as conn:
        max_date = conn.execute(text(query)).scalar()
        
    if not max_date:
        logger.warning("Data Quality Warning: La tabla está vacía, no se puede verificar frescura.")
        return

    # Convertir a datetime si es string (depende del driver/tipo en DB, sqlalchemy suele devolver datetime)
    if isinstance(max_date, str):
        max_date = datetime.fromisoformat(max_date)

    now = datetime.now().date()
    # Si max_date es datetime, extraer date. Si es date, usarlo directo.
    if isinstance(max_date, datetime):
        max_date = max_date.date()
    elif isinstance(max_date, str):
        # Fallback si viene como string
        max_date = datetime.fromisoformat(max_date).date()
    
    diff = now - max_date
    
    if diff.days > max_days_lag:
        msg = f"FALLÓ Data Quality Check: Los datos están desactualizados. Última fecha: {max_date}. Retraso: {diff.days} días."
        logger.error(msg)
        raise ValueError(msg)
        
    logger.info(f"PASÓ: Datos frescos. Última fecha: {max_date}")

def run_all_checks(engine):
    """
    Ejecuta todas las validaciones de calidad de datos.
    """
    logger.info("--- Iniciando Checks de Calidad de Datos ---")
    try:
        check_no_nulls(engine)
        check_duplicates(engine)
        check_data_freshness(engine)
        logger.info("--- Todos los Checks de Calidad PASARON exitosamente ---")
    except Exception as e:
        logger.error(f"Data Quality Check FALLÓ: {e}")
        raise e
