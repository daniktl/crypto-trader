# source https://huobiapi.github.io/docs/spot/v1/en/#authentication

from engine.traders.huobi_trader import HuobiTrader

API_KEY = "e2xxxxxx-99xxxxxx-84xxxxxx-7xxxx"
TIMESTAMP = "2017-05-11T15%3A19%3A30"
SIGNATURE = "Q2eSmGtu3IscVgixbcr/u9yvPFyrLRkF7hRm5PksIyE="


def test_huobi_sign_request_body():
    trader = HuobiTrader(api_key=API_KEY, secret_key="1")
    res = trader.sign_request_body("GET", "/new", {"order_id": 1, "Timestamp": TIMESTAMP})
    expected_signature = SIGNATURE
    assert res["Signature"] == expected_signature
