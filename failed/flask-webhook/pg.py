from binance.client import Client
import pickle as pickle



def read_dictionary_from_file(fn):
    try:
        with open(fn, 'r') as file:
            lines = file.readlines()

        dictionary = {}
        for line in lines:
            key, value = line.strip().split(': ')
            dictionary[key] = value

        return dictionary
    except Exception as e:
        print(f"Failed to read file and convert to dictionary: {e}")
        return None

def write_dictionary_to_file(dictionary, fn):
    try:
        old_val = read_dictionary_from_file(fn)
        for k in dictionary:
            old_val[k] = dictionary[k]
        with open(fn, 'w') as file:
            for key, value in old_val.items():
                file.write(f"{key}: {value}\n")
        print("Dictionary successfully written to position_logs.txt.")
    except Exception as e:
        print(f"Failed to write dictionary to file: {e}")

def get_client():
    fn = '/home/azureuser/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()

def get_open_position():
    # Retrieve account information
    account_info = client.futures_account()
    last_order_side = read_dictionary_from_file('position_logs.txt')['side']

    for val in account_info['positions']:
        if float(val['entryPrice']) != 0.0:
            return last_order_side

    return None


def get_entry_price(order_id):
    try:
        order = client.futures_get_order(symbol='BTCUSDT', orderId=order_id)
        entry_price = float(order['avgPrice'])
        return entry_price
    except Exception as e:
        print(f"Failed to retrieve entry price: {e}")
        return None

def create_tp_order():
    last_order = read_dictionary_from_file('position_logs.txt')
    last_order_entry_price = get_entry_price(last_order['order_id'])
    config = read_dictionary_from_file('config.txt')
    tp1 = float(config['tp1'])
    qty = float(config['qty'])
    leverage = int(config['leverage'])
    if last_order['side'] == 'BUY':
        tp1_price = int(last_order_entry_price*(1+(tp1/100)))

        new_side = 'SELL'
    if last_order['side'] == 'SELL':
        tp1_price = int(last_order_entry_price*(1-(tp1/100)))

        new_side = 'BUY'
    execute_limit_order(new_side, 'BTCUSDT', round(qty, 3), tp1_price)
    print(last_order_entry_price)

def execute_limit_order(side, symbol, quantity, price):
    config = read_dictionary_from_file('config.txt')
    leverage = int(config['leverage'])
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side.upper(),
            type='LIMIT',
            timeInForce='GTC',  # Good 'til Cancelled
            quantity=quantity,
            price=price,
            leverage=leverage
        )
        print(f"Limit order executed: {side} {quantity} {symbol} at price {price}. Order ID: {order['orderId']}")
        return order
    except Exception as e:
        print(f"Failed to execute limit order: {e}")
        return None


def execute_market_order(side, symbol, quantity):
    config = read_dictionary_from_file('config.txt')
    leverage = int(config['leverage'])
    try:
        order = client.futures_create_order(symbol=symbol, side=side.upper(), type='MARKET', quantity=quantity, leverage=leverage)
        write_dictionary_to_file({'side': side.upper(), 'order_id': order['orderId']}, 'position_logs.txt')
        print(f"Order executed: {side} {quantity} {symbol} at market price. Order ID: {order['orderId']}")
        return order
    except Exception as e:
        print(f"Failed to execute order: {e}")
        return None


def cancel_all_orders():
    try:
        open_orders = client.futures_get_open_orders()
        for order in open_orders:
            order_id = order['orderId']
            client.futures_cancel_order(symbol='BTCUSDT', orderId=order_id)
            print(f"Order {order_id} cancelled.")
    except Exception as e:
        print(f"Failed to cancel orders: {e}")

def close_all_positions():
    new_side = 'BUY' if read_dictionary_from_file('position_logs.txt')['side'] == 'SELL' else 'SELL'
    print(new_side)
    # Retrieve account information
    account_info = client.futures_account()

    # Get a list of open positions
    open_positions = [position for position in account_info['positions'] if float(position['entryPrice']) != 0.0]

    for i in open_positions:
        # print(new_side, i['symbol'], float(abs(i['positionAmt'])))
        execute_market_order(new_side, i['symbol'], abs(float(i['positionAmt'])))
    cancel_all_orders()


def get_futures_wallet_balance():
    try:
        account_info = client.futures_account()
        total_balance = float(account_info['totalWalletBalance'])
        return account_info
    except Exception as e:
        print(f"Failed to retrieve futures wallet balance: {e}")
        return None
a=get_futures_wallet_balance()
for i in a:
    print(i, a[i])