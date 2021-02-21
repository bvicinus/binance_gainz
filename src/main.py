import argparse 
import json
import os
import pathlib
from binance.client import Client
from datetime import datetime
# local imports 
from settings import config
import calculate
import cmc

saveOrdersFile = False
FIAT = 'USD'

tld = config['top_level_domain']
client = Client(config['binance_api_key'], 
                config['binance_api_secret'] ,
                tld=tld)

def parse_args():
    parser = argparse.ArgumentParser(description='Binance Gainz Calculator')
    parser.add_argument('-s', '--symbol', type=str, default='BTC',
                        help='Enter the Crypto symbol (do not include "USD")')
    args = parser.parse_args()
    return args

def get_symbol_with_fiat(symbol: str) -> str:
    fiat_with_symbol = f'{symbol}{FIAT}'
    return fiat_with_symbol

def store_historical_data(fiat_symbol: str, 
                          quantity: float, 
                          current_price: float,
                          equity: float,
                          gainz: float) -> None:
    data = {
        'fiat_symbol':fiat_symbol,
        'quantity': quantity,
        'current_price': current_price,
        'equity': equity,
        'gainz': gainz,
        'timestamp': datetime.now().replace(microsecond=0).isoformat(),
        'timestamp_utc': datetime.utcnow().replace(microsecond=0).isoformat(),
    }

    if not os.path.exists('data'):
        os.mkdir('data')
    file_path = os.path.join('data', f'{fiat_symbol}_history.json')
    if not os.path.exists(file_path):
        pathlib.Path(file_path).touch()
    
    with open(file_path, 'a') as f:
        f.write(f'{json.dumps(data)},\n')

def get_orders(fiat_symbol: str):
    orders = client.get_all_orders(symbol=fiat_symbol)
    if saveOrdersFile:
        with open(os.path.join('data', 'orders.json'), 'w') as f:
            f.write(json.dumps(orders, indent=2, separators=(',', ': ')))
    print('Finished gathering all orders')
    return orders
        

def main(symbol: str):
    status = client.get_system_status()
    if status.get('status') != 0:
        raise Exception(f'Binance.{tld} is offline')

    fiat_symbol = get_symbol_with_fiat(symbol=symbol)
    print(f'Running calculations with [{fiat_symbol}]')
    account = client.get_account()
    balances = account.get('balances', [])
    crypto_free = next((b.get('free') for b in balances if b.get('asset') == symbol), None)
    print(f'How much {symbol} owned right now: [{crypto_free}]')

    orders = get_orders(fiat_symbol=fiat_symbol)

    crypto_price = cmc.get_crypto_price(ticker=symbol)
    print(f'Current {fiat_symbol} price: [${crypto_price}]')

    equity = calculate.equity(price=float(crypto_price), quantity=float(crypto_free))
    print(f'Your equity in {fiat_symbol}: [${equity}]')

    gainz = calculate.unrealized_gains(order_list=orders, current_price=crypto_price, ticker=fiat_symbol)
    print(f'these are your {fiat_symbol} gainz [${gainz}]')
    
    store_historical_data(fiat_symbol=fiat_symbol,
                          quantity=crypto_free,
                          current_price=crypto_price,
                          equity=equity,
                          gainz=gainz)


if __name__ == '__main__':
    args = parse_args()
    main(symbol=args.symbol)
