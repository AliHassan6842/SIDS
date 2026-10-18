class ImageRejected(ValueError):
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


class ModelUnavailable(RuntimeError):
    pass
