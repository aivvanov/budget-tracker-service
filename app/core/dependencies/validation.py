class ValidationException(Exception):
    def __init__(self, field: str, min_length: int):
        self.field = field
        self.min_length = min_length
