import logging
import sys

def setup_logger(name: str = "crypto_analytics") -> logging.Logger:
    """
    Configura y devuelve un logger con un formato estandarizado.
    
    Args:
        name (str): El nombre del logger.

    Returns:
        logging.Logger: Instancia de logger configurada.
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya existen
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Crear handler de consola
        c_handler = logging.StreamHandler(sys.stdout)
        
        # Definir el formato
        # Ejemplo: 2023-10-27 10:00:00,123 - crypto_analytics - INFO - Mensaje de log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        
        # Añadir handler al logger
        logger.addHandler(c_handler)
        
    return logger
