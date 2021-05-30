import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config

CRYPTO_SYMBOL_SOCKET = 'ethusdt'  # test with Ethereum
time_interval = '1m'  # 1 minute candle stick
BINANCE_SOCKET_ENDPOINT = f'wss://stream.binance.com:9443/ws/{CRYPTO_SYMBOL_SOCKET}@kline_{time_interval}'

RSI_PERIOD = 14  # default from text book is 14 days
RSI_OVERBOUGHT = 50  # default RSI OVERBOUGHT is 70%
RSI_OVERSOLD = 40  # default RSI OVERSOLD is 30%
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.00875  # 20 USD = 0.00875 ETH, for testing only

closes = []
in_position = False

binance_client = Client(config.API_KEY, config.API_SECRET, tld='us')


def orderAtMarketPrice(symbol, quantity, side):
    try:
        print('Sending Market Order')
        order = binance_client.create_test_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,  # ORDER_TYPE_MARKET is at the market price while ORDER_TYPE_LIMIT is limit price
            quantity=quantity
        )
        print(order)
    except Exception as e:
        print(e)
        return False

    return True


# def orderAtLimitPrice(symbol, quantity, side, limitPrice):
#
#     try:
#         print('Sending Limit Order')
#         order = binance_client.create_test_order(
#             symbol=symbol,
#             side=side,
#             type=ORDER_TYPE_LIMIT,  # ORDER_TYPE_MARKET is at the market price while ORDER_TYPE_LIMIT is limit price
#             quantity=quantity,
#             price=limitPrice
#         )
#         print(order)
#     except Exception as e:
#         print(e)
#         return False
#
#     return True


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_error(ws, error):
    print('Error: ' + error)


def on_message(ws, message):
    global closes, in_position

    # print('Message: '+message)
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed is True:
        print('Candle closed at {}'.format(close))
        closes.append(float(close))
        print("Closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print('all rsis calculated so far')
            print(rsi)
            last_rsi = rsi[-1]  # last RSI
            print(' the current rsi is {}'.format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:

                if in_position is True:
                    print('Action: RSI_OVERBOUGHT, Sell!!!')
                    # Binance sell order logic here
                    side = SIDE_SELL
                    sellOrder_succeeded = orderAtMarketPrice(TRADE_SYMBOL, TRADE_QUANTITY, side)

                    if sellOrder_succeeded:
                        in_position = False

                else:
                    print("Action: It is overbought, but we don't own any. Nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                if in_position is True:
                    print("Action: it is oversold, but you already own it, nothing to do.")
                else:
                    print('Action: RSI_OVERSOLD, Buy!!!')

                    # Binance buy order logic here
                    side = SIDE_BUY
                    buyOrder_succeeded = orderAtMarketPrice(TRADE_SYMBOL, TRADE_QUANTITY, side)

                    if buyOrder_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(BINANCE_SOCKET_ENDPOINT,
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message,
                            on_error=on_error)
ws.run_forever()
