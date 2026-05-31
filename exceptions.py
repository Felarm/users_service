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


class UserNotFoundException(ResourceNotFoundException):
    pass


class SessionNotFoundException(ResourceNotFoundException):
    pass


class TokenException(UnauthorizedException):
    def __init__(self, token_type: str, err_type: str):
        super().__init__(msg="Token error")
        self.token_type = token_type
        self.err_type = err_type
