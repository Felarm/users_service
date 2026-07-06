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


class ResourceConflictException(BaseAppException):
    def __init__(self, msg: str):
        super().__init__(msg, status_code=status.HTTP_409_CONFLICT)


class ForbiddenException(BaseAppException):
    def __init__(self, msg: str):
        super().__init__(msg, status_code=status.HTTP_403_FORBIDDEN)


class UserNotFoundException(ResourceNotFoundException):
    def __init__(self, msg: str = None):
        super().__init__("User not found" if msg is None else msg)


class SessionNotFoundException(ResourceNotFoundException):
    def __init__(self, msg: str = None):
        super().__init__("Session not found" if msg is None else msg)
