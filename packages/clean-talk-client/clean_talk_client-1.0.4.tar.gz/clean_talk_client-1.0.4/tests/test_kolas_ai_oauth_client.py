import unittest
from unittest.mock import patch, Mock
from clean_talk_client.kolas_ai_oauth_client import KolasAiOAuthClient
from clean_talk_client.exception.clean_talk_exception import CleanTalkException
from clean_talk_client.auth_result import AuthResult
import requests

class TestKolasAiOAuthClient(unittest.TestCase):
    ACCESS_TOKEN = 'token123'
    EXPIRES_IN = 3600
    SCOPE = 'scope1'
    TOKEN_TYPE = 'Bearer'

    def setUp(self):
        self.client = KolasAiOAuthClient()
        self.client_id = 'test_id'
        self.client_secret = 'test_secret'

    @patch('clean_talk_client.kolas_ai_oauth_client.requests.Session.post')
    def test_auth_success(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'access_token': self.ACCESS_TOKEN,
            'token_type': self.TOKEN_TYPE,
            'expires_in': self.EXPIRES_IN
        }
        mock_post.return_value = mock_response
        result = self.client.auth(self.client_id, self.client_secret)
        self.assertIsInstance(result, AuthResult)
        self.assertEqual(result.access_token, self.ACCESS_TOKEN)
        self.assertEqual(result.token_type, self.TOKEN_TYPE)
        self.assertEqual(result.expires_in, self.EXPIRES_IN)

    @patch('clean_talk_client.kolas_ai_oauth_client.requests.Session.post')
    def test_auth_missing_access_token(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'error': 'invalid'}
        mock_post.return_value = mock_response
        with self.assertRaises(CleanTalkException):
            self.client.auth(self.client_id, self.client_secret)

    @patch('clean_talk_client.kolas_ai_oauth_client.requests.Session.post')
    def test_auth_http_error(self, mock_post):
        mock_post.side_effect = requests.RequestException('Network error')
        with self.assertRaises(CleanTalkException):
            self.client.auth(self.client_id, self.client_secret)

    @patch('clean_talk_client.kolas_ai_oauth_client.requests.Session.post')
    def test_auth_invalid_client_id(self, mock_post):
        # None as client_id
        with self.assertRaises(CleanTalkException):
            self.client.auth(None, self.client_secret)
        # Empty string as client_id
        with self.assertRaises(CleanTalkException):
            self.client.auth('', self.client_secret)
        # Whitespace string as client_id
        with self.assertRaises(CleanTalkException):
            self.client.auth('   ', self.client_secret)

    @patch('clean_talk_client.kolas_ai_oauth_client.requests.Session.post')
    def test_auth_invalid_client_secret(self, mock_post):
        # None as client_secret
        with self.assertRaises(CleanTalkException):
            self.client.auth(self.client_id, None)
        # Empty string as client_secret
        with self.assertRaises(CleanTalkException):
            self.client.auth(self.client_id, '')
        # Whitespace string as client_secret
        with self.assertRaises(CleanTalkException):
            self.client.auth(self.client_id, '   ')

if __name__ == '__main__':
    unittest.main()
