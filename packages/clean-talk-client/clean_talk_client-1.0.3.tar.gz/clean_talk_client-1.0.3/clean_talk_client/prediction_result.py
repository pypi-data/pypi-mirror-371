from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class PredictionResult:
    def __init__(self, message_id, message, categories, prediction, probability):
        self.message_id = message_id
        self.message = message
        self.categories = categories
        self.prediction = prediction
        self.probability = probability

    @classmethod
    def from_dict(cls, data):
        if not all(k in data and data[k] for k in ('messageId', 'message', 'prediction', 'probability', 'categories')):
            raise CleanTalkException('Invalid data for PredictionResult')
        return cls(
            message_id=data['messageId'],
            message=data['message'],
            categories=list(data['categories']),
            prediction=data['prediction'],
            probability=float(data['probability'])
        )

    def get_message_id(self):
        return self.message_id

    def get_message(self):
        return self.message

    def get_categories(self):
        return self.categories

    def get_prediction(self):
        return self.prediction

    def get_probability(self):
        return self.probability
