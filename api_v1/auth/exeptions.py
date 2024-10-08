from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class UnauthedExpeption(HTTPException):
    """
    Исключение поднятое авторизацией
    """

    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: Any = 'Ошибка авторизации',
        headers: Optional[Dict[str, str]] = {'WWW-Authenticate': 'Basic'},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidAlgorithm(ValueError):
    """
    Не верный агоритм
    """

    pass
