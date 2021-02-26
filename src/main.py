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

SAVE_ORDERS = False
FIAT = 'USD'
TLD = config['top_level_domain']
client = Client(config['binance_api_key'], 
                config['binance_api_secret'] ,
                tld=TLD)

def parse_args():
    parser = argparse.ArgumentParser(description='Binance Gainz Calculator')
    parser.add_argument('-s', '--symbol', type=str, default=None,
                        help='To only calculate gainz for 1 symbol, specify the crypto symbol (do not include "USD")')
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
        'symbol':fiat_symbol,
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
    if SAVE_ORDERS:
        with open(os.path.join('data', f'{fiat_symbol}_orders.json'), 'w') as f:
            f.write(json.dumps(orders, indent=2, separators=(',', ': ')))
    return orders
        

def main(symbol=None):
    status = client.get_system_status()
    if status.get('status') != 0:
        raise Exception(f'Binance.{TLD} is offline')

    account = client.get_account()
    balances = account.get('balances', [])
    gainz = 0.0
    for balance in balances:
        if symbol is None and float(balance.get('free', 0)) > 0:
            gainz += calculate_gainz(holding=balance)
        elif symbol == balance.get('asset'):  # symbol is not None
            gainz = calculate_gainz(holding=balance)
            print(f'\n{symbol} Gainz: [${gainz:.2f}]\n'.format(symbol, gainz))
            return
    print('\nTotal Gainz: [${:.2f}]\n'.format(gainz))

def calculate_gainz(holding: dict) -> float:
    symbol = holding.get('asset')
    quantity = float(holding.get('free', 0))
    print(f'\nRunning calculations with [{symbol}]')
    print(f'How much [{symbol}] owned right now: [{quantity}]')
    if symbol == FIAT:
        store_historical_data(fiat_symbol=FIAT,
                          quantity=quantity,
                          current_price=1,
                          equity=quantity,
                          gainz=0)
        return 0.0

    fiat_symbol = get_symbol_with_fiat(symbol=symbol)
    crypto_price = cmc.get_crypto_price(ticker=symbol)
    print('Current [{}] price: [${:.2f}]'.format(fiat_symbol, crypto_price))

    equity = calculate.equity(price=float(crypto_price), quantity=quantity)
    print('Your equity in [{}]: [${:.2f}]'.format(fiat_symbol, equity))

    orders = get_orders(fiat_symbol=fiat_symbol)
    gainz = calculate.unrealized_gains(order_list=orders, current_price=crypto_price, ticker=fiat_symbol)
    print('These are your [{}] gainz [${:.2f}]'.format(fiat_symbol, gainz))
    
    store_historical_data(fiat_symbol=fiat_symbol,
                          quantity=quantity,
                          current_price=crypto_price,
                          equity=equity,
                          gainz=gainz)
    return gainz                          


if __name__ == '__main__':
    args = parse_args()
    main(symbol=args.symbol)
