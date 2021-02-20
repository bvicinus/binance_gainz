import os 
import json
from dotenv import load_dotenv
from binance.client import Client
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError


# todo move to settings.py file
load_dotenv()

top_level_domain = os.getenv('TLD', 'us')
api_key = os.getenv('BINANCE_API_KEY', None)
api_secret = os.getenv('BINANCE_API_SECRET', None)
cmc_api_key = os.getenv('COINMARKETCAP_API_KEY', None)

if None in (api_key, api_secret, cmc_api_key):
    raise Exception('Missing some required API keys...')

client = Client(api_key, api_secret, tld=top_level_domain)

status = client.get_system_status()
if status.get('status') != 0:
    raise Exception(f'Binance.{top_level_domain} is offline')

print(f'system is [{status}]')

# info = client.get_exchange_info()
# with open('info.json', 'w') as f:
#     f.write(str(info))

account = client.get_account()
# print(f'account /[{account}]')
balances = account.get('balances', [])
btc_free = next((b.get('free') for b in balances if b.get('asset') == 'BTC'), None)
print(f'How much Bitcoin owned right now: [{btc_free}]')

orders = client.get_all_orders(symbol='BTCUSD')
# print(f'found all orders here: [{orders}]')
with open('orders.json', 'w') as f:
    f.write(json.dumps(orders, indent=2, separators=(',', ': ')))
print('finished gathering all orders')

cmc = CoinMarketCapAPI(cmc_api_key)

r = cmc.cryptocurrency_info(symbol='BTC')
print(f'btc stuff: [{r.data}]')

