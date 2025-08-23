import os


class Token:
    def __init__(self, client):
        self.user = os.getenv("BI_USER")
        self.password = os.getenv("BI_PASSWORD")
        self.grant_type = os.getenv("BI_GRANT_TYPE")
        self.scope = os.getenv("BI_SCOPE")
        self.client_id = os.getenv("BI_CLIENT_ID")
        self.client_secret = os.getenv("BI_CLIENT_SECRET")
        self.client = client
        self.path = "/apidata/token"
        self._create()

    @property
    def token(self):
        return f"{self.token_type} {self.access_token}"

    def _create(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": self.grant_type,
            "username": self.user,
            "password": self.password,
            "scope": self.scope,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = self.client.send_request("POST", self.path, params, headers)
        response = response.json()
        self.token_type = response.get("token_type")
        self.access_token = response.get("access_token")
