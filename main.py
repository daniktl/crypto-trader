import json

from engine.traders.binance_trader import BinanceTrader

if __name__ == '__main__':
    trader = BinanceTrader()
    data = trader.get_exchange_info()
    with open("tmp.json", "w") as f:
        f.write(json.dumps(data))
