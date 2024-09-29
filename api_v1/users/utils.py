from pydantic import BaseModel
from fastapi import HTTPException, status

from api_v1.auth.utils import get_hash_password


class PasswordsHandler(BaseModel):
    """Проверяет валидность паролей и возвращает
    хешированный пароль

    Args:
        password1 (str): Первый пароль
        password2 (str): Повторный пароль
    """
    password1: str
    password2: str
    

    def _check_leng_password(self, password: str):
        """
        Проверка длины пароля
        """
        if len(password) < 7:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(password='Пароль слишком короткий'),
                                )
    
    def _check_similar_password(self,
                                password1:str,
                                password2: str,
                                ):
        """
        Проверка одинаковых паролей
        """
        if password1 != password2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(password1='Пароли не совпали'),
                                )
        self._check_leng_password(password=password1)
    
    def _hash_password(self,
                       password: str,
                       ) -> bytes:
        """Хеширования пароля
        """
        hash_password = get_hash_password(password=password)
        return hash_password

    def get_hash_password(self) -> bytes:
        """
        Возвращает хешированный пароль
        """
        self._check_similar_password(password1=self.password1,
                                     password2=self.password2,
                                     )
        self._check_leng_password(password=self.password1)
        hash_password: bytes = self._hash_password(password=self.password1)
        return hash_password
