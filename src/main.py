import os 
import json
from dotenv import load_dotenv
from binance.client import Client
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from settings import config
import calculate

tld = config['top_level_domain']
client = Client(config['binance_api_key'], 
                config['binance_api_secret'] ,
                tld=tld)

status = client.get_system_status()
if status.get('status') != 0:
    raise Exception(f'Binance.{tld} is offline')

account = client.get_account()
balances = account.get('balances', [])
btc_free = next((b.get('free') for b in balances if b.get('asset') == 'BTC'), None)
print(f'How much Bitcoin owned right now: [{btc_free}]')

orders = client.get_all_orders(symbol='BTCUSD')
with open('orders.json', 'w') as f:
    f.write(json.dumps(orders, indent=2, separators=(',', ': ')))
print('finished gathering all orders')

cmc = CoinMarketCapAPI(config['cmc_api_key'])

crypto_listings = cmc.cryptocurrency_listings_latest().data
# print(f'btc stuff: [{crypto_listings}]')
btc_price = next((crypto.get('quote', {}).get('USD', {}).get('price')
                  for crypto in crypto_listings 
                  if crypto.get('symbol') == 'BTC'), None)
if btc_price is None:
    raise Exception('btc price is None')                  
print(f'Current BTC/USD price: [{btc_price}]')

equity = calculate.equity(price=float(btc_price), quantity=float(btc_free))
print(f'Your equity in BTC/USD: [{equity}]')
