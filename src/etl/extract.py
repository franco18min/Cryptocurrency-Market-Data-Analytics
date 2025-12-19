from pycoingecko import CoinGeckoAPI
import pandas as pd
import time
from src.config import COINS, DAYS_TO_FETCH, VS_CURRENCY

def fetch_coin_data(coin_id, days=DAYS_TO_FETCH, vs_currency=VS_CURRENCY):
    """
    Obtiene datos históricos de mercado para una moneda específica desde la API de CoinGecko.
    """
    try:
        cg = CoinGeckoAPI()
        # Obtener datos de gráfico de mercado
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
        
        # Crear DataFrame inicial desde precios
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        
        # Añadir volumen y market_cap
        # Nota: CoinGecko devuelve listas [timestamp, value], asumimos que se alinean
        volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
        market_caps = pd.DataFrame(data['market_caps'], columns=['timestamp', 'market_cap'])
        
        # Fusionar por timestamp para estar seguros, aunque el índice suele coincidir
        df = df.merge(volumes, on='timestamp', how='left')
        df = df.merge(market_caps, on='timestamp', how='left')
        
        # Añadir identificador coin_id
        df['coin_id'] = coin_id
        
        return df
    except Exception as e:
        print(f"Error obteniendo datos para {coin_id}: {e}")
        return pd.DataFrame()

def extract_all_coins():
    """
    Itera a través de la lista de monedas configurada (COINS) y obtiene datos para cada una.
    Devuelve un DataFrame concatenado.
    """
    all_data = []
    for coin in COINS:
        print(f"Obteniendo datos para {coin}...")
        df = fetch_coin_data(coin)
        if not df.empty:
            all_data.append(df)
        # Ser amable con la API
        time.sleep(1) 
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()
