class PredictRequest:
    def __init__(self, project_id: str, messages: list):
        self.project_id = project_id
        self.messages = messages

    def get_project_id(self) -> str:
        return self.project_id

    def get_messages(self) -> list:
        return self.messages