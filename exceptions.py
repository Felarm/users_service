from fastapi import status


class BaseAppException(Exception):
    def __init__(self, msg: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.msg = msg
        self.status_code = status_code
        super().__init__(self.msg)


class ResourceNotFoundException(BaseAppException):
    def __init__(self, msg: str):
        super().__init__(msg, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(BaseAppException):
    def __init__(self, msg: str):
        super().__init__(msg, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
        

class UnauthorizedException(BaseAppException):
    def __init__(self, msg: str):
        super().__init__(msg, status_code=status.HTTP_401_UNAUTHORIZED)