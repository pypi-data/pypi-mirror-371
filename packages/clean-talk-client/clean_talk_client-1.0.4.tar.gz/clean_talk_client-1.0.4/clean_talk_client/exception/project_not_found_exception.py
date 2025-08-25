from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class ProjectNotFoundException(CleanTalkException):
    CODE = 'PROJECT_NOT_FOUND'