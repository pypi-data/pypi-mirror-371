import unittest
from unittest.mock import patch, Mock
from clean_talk_client.clean_talk_prediction_client import CleanTalkPredictionClient
from clean_talk_client.exception.clean_talk_exception import CleanTalkException
from clean_talk_client.predict_response import PredictResponse
import requests

class DummyMessage:
    def __init__(self, message_id, text):
        self.message_id = message_id
        self.text = text

class DummyPredictRequest:
    def __init__(self, project_id, messages):
        self.project_id = project_id
        self.messages = messages

class TestCleanTalkPredictionClient(unittest.TestCase):
    def setUp(self):
        self.access_token = 'token123'
        self.client = CleanTalkPredictionClient(self.access_token)
        self.predict_request = DummyPredictRequest('proj1', [DummyMessage('m1', 'hello')])

    @patch('clean_talk_client.clean_talk_prediction_client.requests.Session.post')
    def test_predict_success(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'predictions': []}
        mock_post.return_value = mock_response
        result = self.client.predict(self.predict_request)
        self.assertIsInstance(result, PredictResponse)

    @patch('clean_talk_client.clean_talk_prediction_client.requests.Session.post')
    def test_async_predict_success(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        # Should not raise
        self.client.async_predict(self.predict_request)

    def test_predict_no_access_token(self):
        client = CleanTalkPredictionClient('')
        with self.assertRaises(CleanTalkException):
            client.predict(self.predict_request)

    def test_async_predict_no_access_token(self):
        client = CleanTalkPredictionClient('')
        with self.assertRaises(CleanTalkException):
            client.async_predict(self.predict_request)

    @patch('clean_talk_client.clean_talk_prediction_client.requests.Session.post')
    def test_predict_request_exception(self, mock_post):
        mock_post.side_effect = requests.RequestException('Network error')
        with self.assertRaises(CleanTalkException):
            self.client.predict(self.predict_request)

    @patch('clean_talk_client.clean_talk_prediction_client.requests.Session.post')
    def test_async_predict_request_exception(self, mock_post):
        mock_post.side_effect = requests.RequestException('Network error')
        with self.assertRaises(CleanTalkException):
            self.client.async_predict(self.predict_request)

if __name__ == '__main__':
    unittest.main()

