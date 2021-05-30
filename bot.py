import websocket, json, pprint

CRYPTO_SYMBOL = 'ethusdt'  # test with Ethereum
time_interval = '1m'  # 1 minute candle stick

BINANCE_SOCKET_ENDPOINT = f'wss://stream.binance.com:9443/ws/{CRYPTO_SYMBOL}@kline_{time_interval}'

closes = []


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_error(ws, error):
    print('Error: ' + error)


def on_message(ws, message):
    global closes
    # print('Message: '+message)
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed is True:
        print('Candle closed at {}'.format(close))
        closes.append(float(close))
        print("Closes")
        print(closes)


ws = websocket.WebSocketApp(BINANCE_SOCKET_ENDPOINT,
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message,
                            on_error=on_error)
ws.run_forever()
