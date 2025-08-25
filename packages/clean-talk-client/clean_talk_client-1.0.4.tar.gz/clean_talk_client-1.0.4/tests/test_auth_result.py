import unittest
from clean_talk_client.auth_result import AuthResult
from clean_talk_client.exception.clean_talk_exception import CleanTalkException

class TestAuthResult(unittest.TestCase):
    ACCESS_TOKEN = 'token123'
    EXPIRES_IN = 3600
    SCOPE = 'scope1'
    TOKEN_TYPE = 'Bearer'

    def test_valid_auth_result(self):
        result = AuthResult(self.ACCESS_TOKEN, self.TOKEN_TYPE, self.EXPIRES_IN, self.SCOPE)
        self.assertEqual(result.access_token, self.ACCESS_TOKEN)
        self.assertEqual(result.token_type, self.TOKEN_TYPE)
        self.assertEqual(result.expires_in, self.EXPIRES_IN)
        self.assertEqual(result.scope, self.SCOPE)

    def test_empty_access_token(self):
        with self.assertRaises(CleanTalkException):
            AuthResult('', self.TOKEN_TYPE, self.EXPIRES_IN)
        with self.assertRaises(CleanTalkException):
            AuthResult('   ', self.TOKEN_TYPE, self.EXPIRES_IN)

    def test_empty_token_type(self):
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, '', self.EXPIRES_IN)
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, '   ', self.EXPIRES_IN)

    def test_missing_expires_in(self):
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, self.TOKEN_TYPE, None)

    def test_invalid_expires_in(self):
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, self.TOKEN_TYPE, 0)
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, self.TOKEN_TYPE, -10)
        with self.assertRaises(CleanTalkException):
            AuthResult(self.ACCESS_TOKEN, self.TOKEN_TYPE, 'notanumber')

    def test_from_dict_valid(self):
        data = {
            'access_token': self.ACCESS_TOKEN,
            'token_type': self.TOKEN_TYPE,
            'expires_in': self.EXPIRES_IN,
            'scope': self.SCOPE
        }
        result = AuthResult.from_dict(data)
        self.assertEqual(result.access_token, self.ACCESS_TOKEN)
        self.assertEqual(result.token_type, self.TOKEN_TYPE)
        self.assertEqual(result.expires_in, self.EXPIRES_IN)
        self.assertEqual(result.scope, self.SCOPE)

    def test_from_dict_invalid(self):
        data = {
            'access_token': '',
            'token_type': self.TOKEN_TYPE,
            'expires_in': self.EXPIRES_IN
        }
        with self.assertRaises(CleanTalkException):
            AuthResult.from_dict(data)
        data = {
            'access_token': self.ACCESS_TOKEN,
            'token_type': '',
            'expires_in': self.EXPIRES_IN
        }
        with self.assertRaises(CleanTalkException):
            AuthResult.from_dict(data)
        data = {
            'access_token': self.ACCESS_TOKEN,
            'token_type': self.TOKEN_TYPE,
            'expires_in': None
        }
        with self.assertRaises(CleanTalkException):
            AuthResult.from_dict(data)
        data = {
            'access_token': self.ACCESS_TOKEN,
            'token_type': self.TOKEN_TYPE,
            'expires_in': 'notanumber'
        }
        with self.assertRaises(CleanTalkException):
            AuthResult.from_dict(data)

if __name__ == '__main__':
    unittest.main()
