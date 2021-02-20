import os 
from dotenv import load_dotenv

load_dotenv()

top_level_domain = os.getenv('TLD', 'us')
crypto = os.getenv('CRYPTO', 'BTC')
binance_api_key = os.getenv('BINANCE_API_KEY', None)
binance_api_secret = os.getenv('BINANCE_API_SECRET', None)
cmc_api_key = os.getenv('COINMARKETCAP_API_KEY', None)

if None in (binance_api_key, binance_api_secret, cmc_api_key):
    raise Exception('Missing some required API keys...')

config = {
    'top_level_domain': top_level_domain,
    'binance_api_key': binance_api_key,
    'binance_api_secret': binance_api_secret,
    'cmc_api_key': cmc_api_key,
    'crypto': crypto,
}
