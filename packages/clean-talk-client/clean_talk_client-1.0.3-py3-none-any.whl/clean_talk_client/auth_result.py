class AuthResult:
    def __init__(self, access_token, token_type, expires_in, scope=None):
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.scope = scope

    @classmethod
    def from_dict(cls, data):
        return cls(
            access_token=data.get('access_token'),
            token_type=data.get('token_type'),
            expires_in=data.get('expires_in'),
            scope=data.get('scope')
        )
