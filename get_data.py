from pycoingecko import CoinGeckoAPI
import pandas as pd
#Funcion para obetener los datos de la api de coingecko
def get_coin_data(coin, days):
    #Carga de datos
    cg = CoinGeckoAPI()
    data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=days)
    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df['volume'] = pd.DataFrame(data['total_volumes'])[1]
    df['market_cap'] = pd.DataFrame(data['market_caps'])[1]
    df['price_change_24h'] = df['price'].pct_change(periods=1)*100
    df['price_change_7d'] = df['price'].pct_change(periods=7)*100
    df['price_change_30d'] = df['price'].pct_change(periods=30)*100
    df['market_cap_change_24h'] = df['market_cap'].pct_change(periods=1)*100
    df['market_cap_change_7d'] = df['market_cap'].pct_change(periods=7)*100
    df['market_cap_change_30d'] = df['market_cap'].pct_change(periods=30)*100
    df['volume_change_24h'] = df['volume'].pct_change(periods=1)*100
    df['volume_change_7d'] = df['volume'].pct_change(periods=7)*100
    df['volume_change_30d'] = df['volume'].pct_change(periods=30)*100

    return df