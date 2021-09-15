import datetime
import hashlib
import hmac
import os
from typing import Dict

from .base_trader import BaseTrader

BINANCE_API_BASE_URL = "https://api.binance.com"
BINANCE_API_KEY_ENV_NAME = "BINANCE_API_KEY"
BINANCE_SECRET_KEY_ENV_NAME = "BINANCE_SECRET_KEY"

WEB_APPLICATION_FIREWALL_LIMIT = 403
REQUEST_RATE_LIMIT = 429
IP_BANNED = 418

# endpoints
EXCHANGE_INFO_URL = "/api/v3/exchangeInfo"
P2P_ADVERTISERS_API_URL = ""


class BinanceTrader(BaseTrader):

    def __init__(self, **kwargs):
        status_codes_limit = [WEB_APPLICATION_FIREWALL_LIMIT, REQUEST_RATE_LIMIT]
        status_codes_blocked = [IP_BANNED]
        super().__init__(
            name="BinanceTrader",
            api_base_url=BINANCE_API_BASE_URL,
            api_key=kwargs.pop("api_key", None) or os.getenv(BINANCE_API_KEY_ENV_NAME),
            secret_key=kwargs.pop("secret_key", None) or os.getenv(BINANCE_SECRET_KEY_ENV_NAME),
            blocking_status_codes=status_codes_blocked,
            limit_status_codes=status_codes_limit,
        )

    def sign_request_body(self, request_body: Dict) -> Dict:
        """Method to sign request body for the SIGNED endpoints.
        It adds signature and timestamp when it was hashed to the request body.

        :param request_body: request body as key value pairs that has to be sent to the target.

        :return: request body with a signature
        """
        timestamp = datetime.datetime.now().timestamp()
        request_body.setdefault("timestamp", timestamp)
        request_body_str: str = "&".join(f"{k}={v}" for k, v in request_body.items())
        signature = hmac.new(self.secret_key.encode(), request_body_str.encode(), hashlib.sha256).hexdigest()
        request_body["signature"] = signature
        return request_body

    def get_exchange_info(self):
        info = self.get_json(EXCHANGE_INFO_URL)
        return info
