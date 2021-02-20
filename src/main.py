import json
from binance.client import Client
# local imports 
from settings import config
import calculate
import cmc

saveOrdersFile = False
FIAT = 'USD'
CRYPTO = config['crypto']
XCRYPTO = f'{CRYPTO}{FIAT}'

tld = config['top_level_domain']
client = Client(config['binance_api_key'], 
                config['binance_api_secret'] ,
                tld=tld)

status = client.get_system_status()
if status.get('status') != 0:
    raise Exception(f'Binance.{tld} is offline')

account = client.get_account()
balances = account.get('balances', [])
crypto_free = next((b.get('free') for b in balances if b.get('asset') == CRYPTO), None)
print(f'How much {CRYPTO} owned right now: [{crypto_free}]')

orders = client.get_all_orders(symbol=XCRYPTO)
if saveOrdersFile:
    with open('orders.json', 'w') as f:
        f.write(json.dumps(orders, indent=2, separators=(',', ': ')))
print('finished gathering all orders')

crypto_price = cmc.get_crypto_price(ticker=CRYPTO)
print(f'Current {XCRYPTO} price: [{crypto_price}]')

equity = calculate.equity(price=float(crypto_price), quantity=float(crypto_free))
print(f'Your equity in {XCRYPTO}: [{equity}]')

gainz = calculate.unrealized_gains(order_list=orders, current_price=crypto_price, ticker=XCRYPTO)
print(f'these are your {XCRYPTO} gainz [{gainz}]')
