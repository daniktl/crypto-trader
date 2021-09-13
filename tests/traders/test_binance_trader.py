import pytest


TEST_BODY = "symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559"


def test_binance_trader_sign_request_body(binance_trader):
    res = binance_trader.sign_request_body(TEST_BODY)
    assert res == "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"
