from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from settings import config

def get_crypto_price(ticker: str) -> float:
    cmc = CoinMarketCapAPI(config['cmc_api_key'])

    crypto_listings = cmc.cryptocurrency_listings_latest().data

    crypto_price = next((crypto.get('quote', {}).get('USD', {}).get('price')
                        for crypto in crypto_listings 
                        if crypto.get('symbol') == ticker), None)
    if crypto_price is None:
        raise Exception(f'{ticker} price is None')                  
    
    return float(crypto_price)
