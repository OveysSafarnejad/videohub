from fastapi import status
from fastapi.exceptions import HTTPException


class LoginRequiredException(HTTPException):

    def __init__(self, _status_code: int=status.HTTP_401_UNAUTHORIZED, _detail: str=None, *args, **kwargs):
        super().__init__(status_code=_status_code, detail=_detail, *args, **kwargs)


class UserAlreadyExistException(Exception):
    """
        user already exist
    """


class InvalidEmailAddressException(Exception):
    """
        Email invalid
    """


class UserDoesNotExistException(Exception):
    """
        user does not exist
    """