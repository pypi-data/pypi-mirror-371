import requests
from clean_talk_client.request_exception_handler import RequestExceptionHandler
from clean_talk_client.exception.account_balance_empty_exception import AccountBalanceEmptyException
from clean_talk_client.exception.clean_talk_exception import CleanTalkException
from clean_talk_client.exception.project_dataset_not_configured_exception import \
    ProjectDatasetNotConfiguredException
from clean_talk_client.exception.project_not_active_exception import ProjectNotActiveException
from clean_talk_client.exception.project_not_found_exception import ProjectNotFoundException
from clean_talk_client.predict_response import PredictResponse


class CleanTalkPredictionClient:
    BASE_URL = 'https://app.kolas.ai'
    SYNC_PREDICT_ENDPOINT = '/api/v1/predictions/predict'
    ASYNC_PREDICT_ENDPOINT = '/api/v1/predictions/asyncPredict'

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def predict(self, predict_request):
        if not self.access_token:
            raise CleanTalkException('Not authorized. Call auth() first.')

        try:
            resp = self.session.post(
                self.BASE_URL + self.SYNC_PREDICT_ENDPOINT,
                json=self.map_predict_request_to_body(predict_request)
            )
            resp.raise_for_status()

            return PredictResponse.from_dict(resp.json())
        except requests.exceptions.RequestException as e:
            RequestExceptionHandler.handle(e)

    def async_predict(self, predict_request):
        if not self.access_token:
            raise CleanTalkException('Not authorized. Call auth() first.')

        try:
            resp = self.session.post(
                self.BASE_URL + self.ASYNC_PREDICT_ENDPOINT,
                json=self.map_predict_request_to_body(predict_request)
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            RequestExceptionHandler.handle(e)

    def map_predict_request_to_body(self, predict_request):
        return {
            'projectId': predict_request.project_id,
            'messages': [
                {
                    'messageId': m.message_id,
                    'message': m.text,
                } for m in predict_request.messages
            ]
        }
