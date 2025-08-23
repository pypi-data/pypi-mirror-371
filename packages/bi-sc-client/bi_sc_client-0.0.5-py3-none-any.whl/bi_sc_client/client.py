import logging
import os
import urllib

import requests

from bi_sc_client.errors import ErrorApiResponse

_logger = logging.getLogger(__name__)


class BISomConnexioClient:
    def __init__(self):
        self.url = os.getenv("BI_URL")

    def send_request(self, method, path, content, headers={}):
        headers.update({"accept": "application/json"})

        url = urllib.parse.urljoin(self.url, path)

        _logger.debug(
            f"{method} request with:\n- URL: {url}\n- content: {content}\n-headers: {headers}"
        )
        if method == "GET":
            response = requests.get(
                url=url,
                params=content,
                headers=headers,
            )
        elif method == "POST":
            response = requests.post(
                url=url,
                data=content,
                headers=headers,
            )
        elif method == "PUT":
            response = requests.put(
                url=url,
                data=content,
                headers=headers,
            )

        _logger.debug(f"Response status code: {response.status_code}")
        if not response.ok or response.status_code != 200:
            raise ErrorApiResponse(response.text)
        return response
