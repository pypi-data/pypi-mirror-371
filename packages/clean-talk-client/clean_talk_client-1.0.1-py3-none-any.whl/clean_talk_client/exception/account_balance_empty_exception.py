from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class AccountBalanceEmptyException(CleanTalkException):
    CODE = 'ACCOUNT_BALANCE_EMPTY'
