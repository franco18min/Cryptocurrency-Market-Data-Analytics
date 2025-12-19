import os
from dotenv import load_dotenv

load_dotenv()

# Lista de monedas a obtener
COINS = [
    'bitcoin',
    'ethereum',
    'cardano',
    'binancecoin',
    'uniswap',
    'ripple',
    'solana',
    'polkadot',
    'dogecoin'
]

# Configuraciones de API
DAYS_TO_FETCH = 365  # Limitar a 365 días para el plan gratuito de la API
VS_CURRENCY = 'usd'

# Configuraciones de Base de Datos
# Prioridad: 
# 1. Variable de entorno DATABASE_URL (común en proveedores Cloud como Railway/Render)
# 2. Construido desde componentes individuales (común para local/Docker)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'crypto_db')
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Asegurar que usamos el driver correcto para SQLAlchemy si no se especifica
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
