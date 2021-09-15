import json
from dotenv import load_dotenv


from engine.traders.binance_trader import BinanceTrader
from engine.traders.huobi_trader import HuobiTrader

if __name__ == '__main__':
    load_dotenv()
    trader = HuobiTrader()
    data = trader.get_offers()
    print(data)
