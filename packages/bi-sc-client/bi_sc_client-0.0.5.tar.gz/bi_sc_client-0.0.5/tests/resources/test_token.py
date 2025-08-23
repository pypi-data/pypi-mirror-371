import os

import mock
import unittest2 as unittest
from bi_sc_client.client import BISomConnexioClient
from bi_sc_client.resources.token import Token

USER = "fakeuser"
PASSWORD = "fakepassword"
URL = "https://fake.url/"


@mock.patch.dict(
    os.environ,
    {
        "BI_USER": USER,
        "BI_PASSWORD": PASSWORD,
        "BI_URL": URL,
    },
    clear=True,
)
class TokenTestCase(unittest.TestCase):
    def test_create_token_ok(self):
        token_str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhcGlvZG9vIiwiZXhwIjoxNzAyODkwOTQyfQ.iwPnXGmQd9Fkxcb-fg_kKYUxjfUHZsSv8gqV2-KwERQ"  # noqa

        BISomConnexioClientMock = mock.create_autospec(BISomConnexioClient)
        client = BISomConnexioClientMock()

        client.send_request.return_value = mock.Mock(spec=["json"])
        client.send_request.return_value.json.return_value = {
            "access_token": token_str,
            "token_type": "bearer",
        }

        token = Token(client)

        assert token.token == f"bearer {token_str}"
        client.send_request.assert_called_once_with(
            "POST",
            token.path,
            {
                "grant_type": None,
                "username": USER,
                "password": PASSWORD,
                "scope": None,
                "client_id": None,
                "client_secret": None,
            },
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
