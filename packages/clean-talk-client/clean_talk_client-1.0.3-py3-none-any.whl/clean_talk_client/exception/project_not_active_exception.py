from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class ProjectNotActiveException(CleanTalkException):
    CODE = 'PROJECT_NOT_ACTIVE'