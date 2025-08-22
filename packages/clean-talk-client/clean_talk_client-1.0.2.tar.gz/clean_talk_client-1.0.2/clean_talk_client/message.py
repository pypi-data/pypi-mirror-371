from clean_talk_client.exception.clean_talk_exception import CleanTalkException


class Message:
    def __init__(self, message_id: str, text: str):
        if not message_id:
            raise CleanTalkException('Message ID cannot be empty.')
        if not text:
            raise CleanTalkException('Message text cannot be empty.')
        self.message_id = message_id
        self.text = text

    def get_message_id(self) -> str:
        return self.message_id

    def get_text(self) -> str:
        return self.text