import json
import logging
import logging.handlers
import os
from typing import Dict, List, Optional, Union
import sys

import requests
from requests import Response

from engine.utils.exceptions import BlockedRequestException, LimitRequestException
from engine.settings import LOGGER_DIR_PATH, LOGGER_MAX_FILE_SIZE, LOGGER_MAX_BACKUP_SIZE


class BaseTrader:

    name: str
    logger: logging.Logger

    api_base_url: str
    api_key: str
    secret_key: str
    headers: Dict[str, Union[str, bool, int]]

    blocking_status_codes: List[int]
    blocking_messages: List[str]
    limit_status_codes: List[int]
    allowed_status_codes: List[int]

    def __init__(
            self,
            name: str,
            api_base_url: str,
            api_key: str,
            secret_key: str,
            headers: Dict[str, Union[str, bool, int]] = None,
            blocking_status_codes: Optional[List[int]] = None,
            blocking_messages: Optional[List[str]] = None,
            limit_status_codes: Optional[List[int]] = None,
            allowed_status_codes: Optional[List[int]] = None,
    ):
        self.name = name

        self.api_base_url = api_base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.headers = headers or {}

        self.blocking_status_codes = blocking_status_codes or []
        self.blocking_messages = blocking_messages or []
        self.limit_status_codes = limit_status_codes or []
        self.allowed_status_codes = allowed_status_codes or []

        self.init_logger()

    def init_logger(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        logger_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # set up console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logger_format)
        self.logger.addHandler(console_handler)
        # set up file handler to store logs - separate log file for each trader
        fh = logging.handlers.RotatingFileHandler(
            filename=os.path.join(LOGGER_DIR_PATH, f"{self.name}.log"),
            maxBytes=LOGGER_MAX_FILE_SIZE, backupCount=LOGGER_MAX_BACKUP_SIZE
        )
        fh.setFormatter(logger_format)
        self.logger.addHandler(fh)

    def get(self, endpoint: str, params: dict = None) -> str:
        """Method to send GET request to the API endpoint.
        Constructing the URL using the api_base_url class attribute

        :param endpoint: full endpoint path starting from the slash
        :return: response text
        """
        r = requests.get(f"{self.api_base_url}{endpoint}", params=params)
        print(r.request.url)
        self.detect_blocking(r)
        return r.text

    def get_json(self, endpoint: str, params: dict = None) -> Dict:
        """Method to send a GET request to the API endpoint and convert response to the JSON.

        :param endpoint: full endpoint path starting from the slash
        :return: response json
        """
        text_response = self.get(endpoint=endpoint, params=params)
        return json.loads(text_response)

    def detect_blocking(self, response: Response) -> None:
        """Method to check if response was blocked or limit was reached

        :param response: requests response

        :raise LimitRequestException: if limit for this API was reached
        :raise BlockedRequestException: if request was blocked
        :raise HTTPError: if status code is not from the range of successful statuses
        """
        if response.status_code in self.limit_status_codes:
            raise LimitRequestException(
                f"Request URL {response.request.url} was blocked because of reached limit."
            )
        elif (
                response.status_code in self.blocking_status_codes
                or self.allowed_status_codes and response.status_code not in self.allowed_status_codes
        ):
            raise BlockedRequestException(
                f"Request URL {response.request.url} was blocked with a status code {response.status_code}"
            )
        elif self.blocking_messages:
            messages_in_response = [message for message in self.blocking_messages if message in response.text]
            if messages_in_response:
                raise BlockedRequestException(
                    f"Request URL {response.request.url} was blocked "
                    f"with the following blocking phrases {messages_in_response}. "
                    f"Full response body: {response.text}"
                )
        # some API use their own success status codes
        if not self.allowed_status_codes:
            response.raise_for_status()
