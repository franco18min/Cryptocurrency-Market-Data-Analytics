import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_engine():
    """
    Crea y devuelve un motor SQLAlchemy usando la variable de entorno DATABASE_URL.
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
    # Asegurar compatibilidad con SQLAlchemy (postgres:// -> postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(database_url)
        return engine
    except Exception as e:
        print(f"Error creando el motor de base de datos: {e}")
        raise e
