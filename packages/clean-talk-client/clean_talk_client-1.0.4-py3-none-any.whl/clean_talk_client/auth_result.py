from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class AuthResult:
    def __init__(self, access_token, token_type, expires_in, scope=None):
        if not access_token or not str(access_token).strip():
            raise CleanTalkException('Access token cannot be empty or whitespace.')
        if not token_type or not str(token_type).strip():
            raise CleanTalkException('Token type cannot be empty or whitespace.')
        if expires_in is None:
            raise CleanTalkException('expires_in is required.')
        try:
            expires_in_int = int(expires_in)
            if expires_in_int <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise CleanTalkException('expires_in must be a positive integer.')
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in_int
        self.scope = scope

    @classmethod
    def from_dict(cls, data):
        return cls(
            access_token=data.get('access_token'),
            token_type=data.get('token_type'),
            expires_in=data.get('expires_in'),
            scope=data.get('scope')
        )
