# source https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#example-1-as-a-request-body
# TEST_BODY = (
#     "symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559"
# )

TEST_BODY = {
    "symbol": "LTCBTC",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "GTC",
    "quantity": 1,
    "price": 0.1,
    "recvWindow": "5000",
    "timestamp": 1499827319559
}


def test_binance_trader_sign_request_body(binance_trader):
    res = binance_trader.sign_request_body(TEST_BODY)
    # source https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#example-1-as-a-request-body
    expected_result = "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"
    assert res["signature"] == expected_result
