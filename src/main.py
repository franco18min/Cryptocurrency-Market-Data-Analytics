import sys
from src.etl.extract import extract_all_coins
from src.transform.clean import clean_data
from src.transform.kpis import calculate_kpis
from src.load.load_db import load_data_to_supabase
from src.utils.logger import setup_logger
from src.data_quality import run_all_checks
from src.db.connection import get_engine

logger = setup_logger("main_pipeline")

def run_pipeline(incremental=False):
    logger.info(f"--- Iniciando Pipeline ETL (Incremental={incremental}) ---")
    
    # 1. Extracción
    logger.info("\n[Paso 1] Extrayendo datos de CoinGecko...")
    raw_df = extract_all_coins()
    logger.info(f"Se extrajeron {len(raw_df)} filas.")
    
    if raw_df.empty:
        logger.warning("No se extrajeron datos. Saliendo.")
        return

    # 2. Transformación (Limpieza)
    logger.info("\n[Paso 2a] Limpiando datos...")
    clean_df = clean_data(raw_df)
    
    # 3. Transformación (KPIs)
    logger.info("[Paso 2b] Calculando KPIs...")
    final_df = calculate_kpis(clean_df)
    
    # Vista previa
    print("\nVista previa de datos:")
    print(final_df[['coin_id', 'date', 'price', 'profitability_30d', 'volatility_30d']].tail())

    # 4. Carga
    logger.info("\n[Paso 3] Cargando datos a Supabase...")
    
    try:
        load_data_to_supabase(final_df, incremental=incremental)
    except Exception as e:
        logger.error(f"Error durante la fase de carga: {e}")
        raise e
        
    # 5. Checks de Calidad de Datos
    logger.info("\n[Paso 4] Ejecutando Checks de Calidad de Datos...")
    try:
        engine = get_engine()
        run_all_checks(engine)
    except Exception as e:
        logger.error(f"Pipeline falló en Data Quality Check: {e}")
        # Dependiendo de la severidad, podemos hacer raise e para fallar el job completamente
        raise e
    
    logger.info("\n--- Pipeline Completado Exitosamente ---")

if __name__ == "__main__":
    # Verificar argumentos
    # Uso: python -m src.main --incremental
    is_incremental = '--incremental' in sys.argv
    run_pipeline(incremental=is_incremental)
