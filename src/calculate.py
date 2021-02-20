
def equity(price: float, quantity: float) -> float:
    return price * quantity

def unrealized_gains(order_list: list, current_price: float, ticker: str = 'BTCUSD') -> float:
    quantity = 0.0
    cost = 0.0
    for order in order_list:
        if order.get('symbol') != ticker:
            print(f'skipping {order.get("symbol")} because it isnt {ticker}')
            continue
        if order.get('status') != 'FILLED':
            continue
        quantity += float(order.get('executedQty'))
        cost += float(order.get('cummulativeQuoteQty'))
    total_equity = equity(price=current_price, quantity=quantity)
    gains = total_equity - cost 
    return gains
