from typing import List

from requests import Response

from engine.utils.exceptions import BlockedRequestException, LimitRequestException


def detect_blocking(
        response: Response,
        blocked_status_codes: List[int] = None,
        limit_status_codes: List[int] = None,
        blocked_messages: List[str] = None
):
    blocked_status_codes = blocked_status_codes or []
    limit_status_codes = limit_status_codes or []
    blocked_messages = blocked_messages or []

    if response.status_code in limit_status_codes:
        raise LimitRequestException(
            f"Request URL {response.request.url} was blocked because of reached limit."
        )
    elif response.status_code in blocked_status_codes:
        raise BlockedRequestException(
            f"Request URL {response.request.url} was blocked with a status code {blocked_status_codes}"
        )
    elif blocked_messages:
        messages_in_response = [message for message in blocked_messages if message in response.text]
        if messages_in_response:
            raise BlockedRequestException(
                f"Request URL {response.request.url} was blocked "
                f"with the following blocking phrases {messages_in_response}. "
                f"Full response body: {response.text}"
            )
