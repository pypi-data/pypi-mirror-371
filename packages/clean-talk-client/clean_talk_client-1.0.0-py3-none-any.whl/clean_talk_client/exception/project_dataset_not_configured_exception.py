from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class ProjectDatasetNotConfiguredException(CleanTalkException):
    CODE = 'PROJECT_DATASET_NOT_CONFIGURED'