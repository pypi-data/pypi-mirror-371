import unittest
from clean_talk_client.prediction_result import PredictionResult
from clean_talk_client.exception.clean_talk_exception import CleanTalkException

class TestPredictionResult(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'messageId': '123',
            'message': 'Test message',
            'categories': ['spam', 'ham'],
            'prediction': 'spam',
            'probability': 0.95
        }

    def test_from_dict_success(self):
        result = PredictionResult.from_dict(self.valid_data)
        self.assertEqual(result.get_message_id(), '123')
        self.assertEqual(result.get_message(), 'Test message')
        self.assertEqual(result.get_categories(), ['spam', 'ham'])
        self.assertEqual(result.get_prediction(), 'spam')
        self.assertEqual(result.get_probability(), 0.95)

    def test_from_dict_missing_field(self):
        data = self.valid_data.copy()
        del data['messageId']
        with self.assertRaises(CleanTalkException):
            PredictionResult.from_dict(data)

    def test_from_dict_empty_field(self):
        data = self.valid_data.copy()
        data['message'] = ''
        with self.assertRaises(CleanTalkException):
            PredictionResult.from_dict(data)

    def test_getters(self):
        result = PredictionResult('id1', 'msg', ['cat1'], 'pred', 0.5)
        self.assertEqual(result.get_message_id(), 'id1')
        self.assertEqual(result.get_message(), 'msg')
        self.assertEqual(result.get_categories(), ['cat1'])
        self.assertEqual(result.get_prediction(), 'pred')
        self.assertEqual(result.get_probability(), 0.5)

if __name__ == '__main__':
    unittest.main()
