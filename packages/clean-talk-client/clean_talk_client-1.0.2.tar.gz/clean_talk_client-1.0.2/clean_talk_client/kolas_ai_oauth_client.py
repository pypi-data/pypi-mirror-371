import requests

from clean_talk_client.auth_result import AuthResult
from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class KolasAiOAuthClient:
    BASE_URL = 'https://app.kolas.ai'
    AUTH_ENDPOINT = '/oauth/token'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})

    def auth(self, client_id: str, client_secret: str) -> AuthResult:
        url = self.BASE_URL + self.AUTH_ENDPOINT
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
        try:
            response = self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            if 'access_token' not in result:
                raise CleanTalkException(f'OAuth2 authentication failed: {result}')
            return AuthResult.from_dict(result)
        except requests.RequestException as e:
            raise CleanTalkException(f'Auth request failed: {e}') from e
