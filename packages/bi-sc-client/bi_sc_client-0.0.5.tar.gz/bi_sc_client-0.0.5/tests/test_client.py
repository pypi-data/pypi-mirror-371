import os
import urllib

import mock
import requests
import unittest2 as unittest
from bi_sc_client.client import BISomConnexioClient
from bi_sc_client.errors import ErrorApiResponse

URL = "https://fake.url/"


@mock.patch.dict(
    os.environ,
    {
        "BI_URL": URL,
    },
    clear=True,
)
# why need clear=True explained here https://stackoverflow.com/a/67477901/248616
@mock.patch("bi_sc_client.client.requests", spec=["get", "post"])
class ClientTestCase(unittest.TestCase):
    def test_send_request_get_ok(self, RequestsMock):
        response_mock = mock.create_autospec(requests.Response)
        RequestsMock.get.return_value = response_mock
        RequestsMock.get.return_value.status_code = 200
        RequestsMock.get.return_value.ok = True

        fake_path = "/fake_path/"
        response = BISomConnexioClient().send_request("GET", fake_path, {}, {})

        assert response == response_mock
        RequestsMock.get.assert_called_once_with(
            url=urllib.parse.urljoin(URL, fake_path),
            params={},
            headers={"accept": "application/json"},
        )

    def test_send_request_post_ok(self, RequestsMock):
        response_mock = mock.create_autospec(requests.Response)
        RequestsMock.post.return_value = response_mock
        RequestsMock.post.return_value.status_code = 200
        RequestsMock.post.return_value.ok = True

        fake_path = "/fake_path/"
        expected_data = {
            "key": "value",
            "other_key": "value",
        }
        response = BISomConnexioClient().send_request(
            "POST", fake_path, expected_data, {"Content-Type": "application/json"}
        )

        assert response == response_mock
        RequestsMock.post.assert_called_once_with(
            url=urllib.parse.urljoin(URL, fake_path),
            data=expected_data,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def test_send_request_ko(self, RequestsMock):
        response_mock = mock.create_autospec(requests.Response)
        response_mock.text = "ERROR!"
        RequestsMock.post.return_value = response_mock
        RequestsMock.post.return_value.status_code = 500
        RequestsMock.post.return_value.ok = False

        fake_path = "/fake_path/"
        with self.assertRaises(ErrorApiResponse) as exception:
            BISomConnexioClient().send_request("GET", fake_path, {})
            assert exception.msg == response_mock.text
