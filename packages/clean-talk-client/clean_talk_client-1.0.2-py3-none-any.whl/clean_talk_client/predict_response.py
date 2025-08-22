from clean_talk_client.prediction_result import PredictionResult


class PredictResponse:
    def __init__(self, predictions=None):
        self._predictions = predictions or []

    @classmethod
    def from_dict(cls, data):
        predictions = []
        if 'predictions' in data and isinstance(data['predictions'], list):
            for item in data['predictions']:
                predictions.append(PredictionResult.from_dict(item))
        return cls(predictions)

    def get_predictions(self):
        return self._predictions
