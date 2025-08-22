import requests

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

        body = {
            'projectId': predict_request.project_id,
            'messages': [
                {
                    'messageId': m.message_id,
                    'message': m.text,
                } for m in predict_request.messages
            ]
        }

        try:
            resp = self.session.post(
                self.BASE_URL + self.SYNC_PREDICT_ENDPOINT,
                json=body,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            # Implement PredictResponse.from_dict as needed

            return PredictResponse.from_dict(data)
        except requests.exceptions.RequestException as e:
            self._handle_request_exception(e)

    def async_predict(self, predict_request):
        if not self.access_token:
            raise CleanTalkException('Not authorized. Call auth() first.')

        body = {
            'projectId': predict_request.project_id,
            'messages': [
                {
                    'messageId': m.message_id,
                    'message': m.text,
                } for m in predict_request.messages
            ]
        }

        try:
            resp = self.session.post(
                self.BASE_URL + self.ASYNC_PREDICT_ENDPOINT,
                json=body,
                timeout=10
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            self._handle_request_exception(e)

    def _handle_request_exception(self, e):
        if hasattr(e, 'response') and e.response is not None:
            status = e.response.status_code
            try:
                error_data = e.response.json()
            except Exception:
                error_data = {}
            if status == 401:
                raise CleanTalkException('Unauthorized: Invalid access token.')
            elif status == 422:
                self._create_exception(error_data)
            elif status == 500:
                raise CleanTalkException('Internal Server Error: Please try again later or contact technical support.')
            else:
                raise CleanTalkException(f"Predict request failed: {e.response.text}")
        raise CleanTalkException(f"Predict request failed: {str(e)}")

    def _create_exception(self, error_data):
        code = error_data.get('errorCode', '0')
        message = error_data.get('message', 'Invalid request data.')
        errors = error_data.get('errors', [])
        if code == ProjectNotFoundException.CODE:
            raise ProjectNotFoundException(message)
        elif code == ProjectDatasetNotConfiguredException.CODE:
            raise ProjectDatasetNotConfiguredException(message)
        elif code == ProjectNotActiveException.CODE:
            raise ProjectNotActiveException(message)
        elif code == AccountBalanceEmptyException.CODE:
            raise AccountBalanceEmptyException(message)
        else:
            raise CleanTalkException(f'Validation Error: {message} {errors}')
