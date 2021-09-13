import pytest

from engine.traders.binance_trader import BinanceTrader


@pytest.fixture()
def binance_trader():
    api_key = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    secret_key = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
    return BinanceTrader(api_key=api_key, secret_key=secret_key)