from typing import Optional, Dict, Any


class TelegramAPIError(Exception):
    def __init__(
        self, description: str, error_code: int, parameters: Optional[Dict[str, Any]]
    ):
        self.description = description
        self.error_code = error_code
        self.parameters = parameters or {}

        super().__init__(f"[{error_code}] {description} | Params: {self.parameters}")