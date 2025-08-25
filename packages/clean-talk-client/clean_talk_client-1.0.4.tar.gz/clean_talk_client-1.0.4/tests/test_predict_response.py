import unittest
from clean_talk_client.predict_response import PredictResponse
from clean_talk_client.prediction_result import PredictionResult
from clean_talk_client.exception.clean_talk_exception import CleanTalkException

class TestPredictResponse(unittest.TestCase):
    def setUp(self):
        self.prediction_dict = {
            'messageId': '1',
            'message': 'Test',
            'categories': ['spam'],
            'prediction': 'spam',
            'probability': 0.9
        }
        self.valid_data = {
            'predictions': [self.prediction_dict]
        }

    def test_from_dict_with_valid_predictions(self):
        response = PredictResponse.from_dict(self.valid_data)
        predictions = response.get_predictions()
        self.assertEqual(len(predictions), 1)
        self.assertIsInstance(predictions[0], PredictionResult)
        self.assertEqual(predictions[0].get_message_id(), '1')

    def test_from_dict_with_empty_predictions(self):
        data = {'predictions': []}
        response = PredictResponse.from_dict(data)
        self.assertEqual(response.get_predictions(), [])

    def test_from_dict_with_missing_predictions(self):
        data = {}
        response = PredictResponse.from_dict(data)
        self.assertEqual(response.get_predictions(), [])

    def test_from_dict_with_invalid_predictions_type(self):
        data = {'predictions': 'notalist'}
        response = PredictResponse.from_dict(data)
        self.assertEqual(response.get_predictions(), [])

    def test_get_predictions_direct(self):
        pred = PredictionResult.from_dict(self.prediction_dict)
        response = PredictResponse([pred])
        self.assertEqual(response.get_predictions(), [pred])

if __name__ == '__main__':
    unittest.main()
