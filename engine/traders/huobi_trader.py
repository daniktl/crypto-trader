import base64
import datetime
import hashlib
import hmac
import os
from typing import Dict, Optional, Tuple
from urllib.parse import quote_plus

from engine.traders.base_trader import BaseTrader


HUOBI_API_BASE_URL = "https://api.huobi.pro"
HUOBI_API_HOST = "api.huobi.pro"

HUOBI_ACCESS_KEY_ENV_NAME = "HUOBI_ACCESS_KEY"
HUOBI_SECRET_KEY_ENV_NAME = "HUOBI_SECRET_KEY"
HUOBI_C2C_ACCOUNT_ID_ENV_NAME = "HUOBI_C2C_ACCOUNT_ID"

HUOBI_SIGNATURE_VERSION = 2
HUOBI_SIGNATURE_METHOD = "HmacSHA256"

OFFER_STATUSES = ("submitted", "filled", "partial-filled", "canceled", "partial-canceled")

# endpoints
ACCOUNT_BALANCE_URL = "/v2/c2c/account"
OFFERS_URL = "/v2/c2c/offers"
OFFER_URL = "/v2/c2c/offer"


class HuobiTrader(BaseTrader):

    def __init__(self, **kwargs):
        super().__init__(
            name="HuobiTrader",
            api_base_url=HUOBI_API_BASE_URL,
            api_key=kwargs.pop("api_key", None) or os.getenv(HUOBI_ACCESS_KEY_ENV_NAME),
            secret_key=kwargs.pop("secret_key", None) or os.getenv(HUOBI_SECRET_KEY_ENV_NAME),
        )

    def sign_request_body(self, method: str, endpoint: str, request_body: Dict) -> Dict:
        """Method to sign the request body.
        Source: https://huobiapi.github.io/docs/spot/v1/en/#authentication

        :param method: request method
        :param endpoint: URL endpoint want to reach
        :param request_body: request body as a dict

        :return: dict with signature, access key ID and timestamp
        """
        request_body.setdefault("AccessKeyId", self.api_key)
        request_body.setdefault("SignatureMethod", HUOBI_SIGNATURE_METHOD)
        request_body.setdefault("SignatureVersion", HUOBI_SIGNATURE_VERSION)
        request_body.setdefault("Timestamp", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))

        request_body = dict(sorted(request_body.items(), key=lambda x: x[0]))
        request_body_text = "&".join(f"{k}={quote_plus(str(v))}" for k, v in request_body.items())
        pre_signed_text = "\n".join((method.upper(), HUOBI_API_HOST, endpoint, request_body_text))

        signature = hmac.new(self.secret_key.encode("utf-8"), pre_signed_text.encode("utf-8"), hashlib.sha256).digest()
        request_body["Signature"] = base64.b64encode(signature).decode()
        return request_body

    def get_account_balance(self, account_id: int = None) -> Dict:
        """Fetch account balance using the endpoint

        :param account_id: your account ID to get balance

        :return: balance information
        """
        request_body = {
            "accountId": account_id or os.getenv(HUOBI_C2C_ACCOUNT_ID_ENV_NAME)
        }
        balance = self.get_json(ACCOUNT_BALANCE_URL, params=request_body)
        return balance

    def get_json(self, endpoint: str, params: dict = None) -> Dict:
        params_signed = self.sign_request_body("GET", endpoint, params)
        return super().get_json(endpoint, params_signed)

    def get_offers(
            self,
            account_id: str = None,
            currency: str = None,
            side: str = None,
            statuses: Tuple[str] = None,
            start_time: int = None,
            end_time: int = None,
            limit: int = None,
            from_offer_id: int = None
    ) -> Dict:
        """Method to query c2c offers.
        Source: https://huobiapi.github.io/docs/spot/v1/en/#query-lending-borrow-offers

        :param account_id:
        :param currency:
        :param side:
        :param statuses:
        :param start_time:
        :param end_time:
        :param limit:
        :param from_offer_id:
        :return: Response from the Huobi
        """
        if not statuses:
            statuses = OFFER_STATUSES
        request_body = {
            "offerStatus": ",".join(statuses)
        }
        offers = self.get_json(OFFERS_URL, request_body)
        return offers

    def post_offer(
            self,
            cc: str,
            side: str,
            amount: str,
            interest_rate: str,
            loan_term: int,
            account_id: str = None,
            time_in_force: str = None
    ) -> Dict:
        """Method to place new offer on th Huobi.

        :param cc: cryptocurrency of new offer
        :param side: lend/borrow
        :param amount: offer value
        :param interest_rate: daily interest rate
        :param loan_term: loan term
        :param account_id:
        :param time_in_force:
        :return: Response from the Huobi
        """
        new_offer_payload = {
            "currency": cc,
            "side": side,
            "amount": amount,
            "interestRate": interest_rate,
            "loadTerm": loan_term
        }
        offer = self.get_json(OFFER_URL, new_offer_payload)
        return offer
