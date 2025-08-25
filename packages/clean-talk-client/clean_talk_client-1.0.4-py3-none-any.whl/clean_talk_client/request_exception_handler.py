from clean_talk_client.exception.account_balance_empty_exception import AccountBalanceEmptyException
from clean_talk_client.exception.clean_talk_exception import CleanTalkException
from clean_talk_client.exception.project_dataset_not_configured_exception import ProjectDatasetNotConfiguredException
from clean_talk_client.exception.project_not_active_exception import ProjectNotActiveException
from clean_talk_client.exception.project_not_found_exception import ProjectNotFoundException

class RequestExceptionHandler:
    @staticmethod
    def handle(e):
        if hasattr(e, 'response') and e.response is not None:
            status = e.response.status_code
            try:
                error_data = e.response.json()
            except Exception:
                error_data = {}
            if status == 401:
                raise CleanTalkException('Unauthorized: Invalid access token.')
            elif status == 422:
                RequestExceptionHandler._create_exception(error_data)
            elif status == 500:
                raise CleanTalkException('Internal Server Error: Please try again later or contact technical support.')
            else:
                raise CleanTalkException(f"Predict request failed: {e.response.text}")
        raise CleanTalkException(f"Predict request failed: {str(e)}")

    @staticmethod
    def _create_exception(error_data):
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

